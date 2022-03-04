#!/bin/bash

# Use empty string for the version to fetch latest CLI version
declare -A AzExtensions=(
    ["arcappliance"]="0.2.16"
    ["connectedvmware"]="0.1.6"
    ["k8s-extension"]="1.0.4"
    ["customlocation"]="0.1.3")

fail () {
   echo 'Execution failed.'
   exit 1
}

activate_python_venv() {
  echo "Activating python venv..."
  source .temp/.env/bin/activate
}

deactivate_python_venv() {
  echo "Deactivating python venv..."
  deactivate
}

check_if_extension_is_installed() {
  name="$1"
  version="$2"
  extensionVersion=$(az version --query "extensions.\"$name\"" -o tsv)
  # extension is not isntalled
  if [ "$extendedVersion" == "" ]
  then
    return 0
  fi
  # Extesnion is installed and extension version is euqal to required version
  if [ "$extensionVersion" == "$version" ]
  then
    return 1
  fi
  return 0
}

install_extensions_if_not_already_installed() {
  name="$1"
  version="$2"
  check_if_extension_is_installed $name $version
  if [ $? == 0 ]
  then
    echo "Installing Az extension $name of version $version..."
    if [ "$version" == "" ]
    then
      az extension add --name "$name" --upgrade
    else
      az extension add --name "$name" --version "$version" --upgrade
    fi
  else
    echo "Extension $name of version $version is already present"
  fi
}

print_operation_status_message() {
  operation_name="$1"
  operation_exit_code="$2"

  RED="\e[0;91m"
  GREEN="\e[0;92m"
  RESET="\e[0m"

  if [ $operation_exit_code -eq 0 ]
  then
    echo -e "${GREEN}$operation_name operation was successfull.${RESET}"
  else
    echo -e "${RED}$operation_name operation failed! Please check stderr or equivalent for more details.${RESET}"
  fi
}

mkdir .temp
if [ ! -z "$2" ] && [ -f "$2" ]
then
  http_p=$(grep -Po '(?<="http": ")[^"]*' "$2")
  https_p=$(grep -Po '(?<="https": ")[^"]*' "$2")
  export http_proxy=$http_p
  export HTTP_PROXY=$http_p
  export https_proxy=$https_p
  export HTTPS_PROXY=$https_p
fi

sudo -E apt-get -y update || fail
sudo -E apt-get -y install jq || fail

if [ ! -z $https_p ]
then
  noproxy=$(cat "$2" | jq -r '.proxyDetails.noProxy')
  export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
fi

if [ ! -z $noproxy ] && [ ! $noproxy == 'null' ]
then
  export no_proxy=$noproxy
  export NO_PROXY=$noproxy
fi

if [ ! -f ".temp/govc" ]
then
  echo "Downloading govc..."
  sudo -E apt-get -y install curl || fail
  sudo -E apt-get -y install gzip || fail
  URL_TO_BINARY="https://github.com/vmware/govmomi/releases/download/v0.24.0/govc_linux_amd64.gz"
  curl -L $URL_TO_BINARY | gunzip > ./.temp/govc
  sudo -E chmod +x ./.temp/govc
fi

( ( az version || (curl -sL https://aka.ms/InstallAzureCLIDeb | sudo -E bash) ) && ( az account get-access-token || az login --use-device-code ) ) || { echo 'az installation or login failed' ; fail; }

for key in "${!AzExtensions[@]}"
do
  name="$key"
  version="${AzExtensions[$key]}"
  install_extensions_if_not_already_installed $name $version
done

echo "Installing python3.8..."
sudo -E apt-get -y install python3.8 || fail
sudo -E apt-get -y install python3.8-venv python3-venv|| fail

echo "Creating python venv..."
python3.8 -m venv .temp/.env || fail


activate_python_venv
python -m pip install --upgrade pip || fail
python -m pip install -r ./appliance_setup/dependencies || fail
python ./appliance_setup/run.py "$1" "$2" "${3:-INFO}"
operation_exit_code=$?
print_operation_status_message $1 $operation_exit_code
deactivate_python_venv

exit $operation_exit_code