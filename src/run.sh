#!/bin/bash

# Use empty string for the version to fetch latest CLI version
declare -A AzExtensions=(
  ["arcappliance"]=""
  ["connectedvmware"]=""
  ["k8s-extension"]=""
  ["customlocation"]="")

RED="\e[0;91m"
GREEN="\e[0;92m"
RESET="\e[0m"

fail() {
  echo -e "${RED}\nScript execution failed: $1\n\n${NC}"
  exit 33
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
  if [ "$extensionVersion" == "" ]
  then
    return 0
  fi
  # Extension is installed and extension version is equal to required version
  if [ "$extensionVersion" == "$version" ]
  then
    return 1
  fi
  return 0
}

install_extensions_if_not_already_installed() {
  name="$1"
  version="$2"
  if [ "$version" == "" ]
    then
      az extension add --name "$name" --upgrade
  else
    check_if_extension_is_installed "$name" "$version"
    if [ $? == 0 ]
      then
        echo "Installing Az extension $name of version $version..."
        az extension add --name "$name" --version "$version" --upgrade
    else
      echo "Extension $name of version $version is already present"
    fi
  fi
}

print_operation_status_message() {
  operation_name="$1"
  operation_exit_code="$2"

  if [ "$operation_exit_code" -eq 0 ]
  then
    echo -e "${GREEN}$operation_name operation was successfull.${RESET}"
  else
    echo -e "${RED}$operation_name operation failed! Please check stderr or equivalent for more details.${RESET}"
  fi
}

mkdir -p .temp
if [ -n "$2" ] && [ -f "$2" ]
then
  http_p=$(grep -A 20 "managementProxyDetails" "$2" | grep -Po '(?<="http": ")[^"]*')
  https_p=$(grep -A 20 "managementProxyDetails" "$2" | grep -Po '(?<="https": ")[^"]*')
  noproxy=$(grep -A 20 "managementProxyDetails" "$2" | grep -Po '(?<="noProxy": ")[^"]*')
  proxyCAInput=$(grep -A 20 "managementProxyDetails" "$2" | grep -Po '(?<="certificateFilePath": ")[^"]*')
  if [[ -n "$proxyCAInput" ]]; then
    proxyCA=$(realpath "$proxyCAInput")
    if [[ -z "$proxyCA" ]]; then
      fail "Invalid path '$proxyCAInput'. Please note that special variables like '~' and '\$HOME' are not expanded. Please provide a valid certificate file path."
    fi
    if [[ ! -f "$proxyCA" ]]; then
      fail "No file exists in the path '$proxyCA'. Please provide a valid certificate file path."
    fi
    echo "Setting REQUESTS_CA_BUNDLE to $proxyCA"
    export REQUESTS_CA_BUNDLE="$proxyCA"
  fi
  export http_proxy=$http_p
  export HTTP_PROXY=$http_p
  export https_proxy=$https_p
  export HTTPS_PROXY=$https_p
  export no_proxy=$noproxy
  export NO_PROXY=$noproxy
fi

if [ ! -f ".temp/govc" ]
then
  echo "Downloading govc..."
  msg="failed to run apt-get or curl command"
  if [[ -n "$REQUESTS_CA_BUNDLE" ]]; then
    msg="Please ensure $REQUESTS_CA_BUNDLE is installed as a root certificate, by running 'sudo cp $REQUESTS_CA_BUNDLE /usr/local/share/ca-certificates/ && sudo update-ca-certificates'"
  fi
  sudo -E apt-get -y update || fail "$msg"
  sudo -E apt-get -y install curl || fail "$msg"
  sudo -E apt-get -y install gzip || fail "$msg"
  URL_TO_BINARY="https://github.com/vmware/govmomi/releases/download/v0.24.0/govc_linux_amd64.gz"
  curl -L $URL_TO_BINARY | gunzip > ./.temp/govc || fail "$msg"
  sudo -E chmod +x ./.temp/govc
fi

( ( az version || (curl -sL https://aka.ms/InstallAzureCLIDeb | sudo -E bash) ) && ( az account get-access-token || az login --use-device-code ) ) || { echo 'az installation or login failed' ; fail; }

for key in "${!AzExtensions[@]}"
do
  name="$key"
  version="${AzExtensions[$key]}"
  install_extensions_if_not_already_installed "$name" "$version"
done

fetchPythonLocation() {
  azVersion=$(az --version 2>&1)
  pythonLoc=$(echo "$azVersion" | grep "^Python location")
  pythonExe=$(echo "$pythonLoc" | sed -E "s/^Python location '(.+?)'/\1/")
  echo "$pythonExe"
}

pythonExe="$(fetchPythonLocation)"
if [ -z "$pythonExe" ]
then
  echo "Python executable not found in az cli"
  fail
fi

echo "Python executable of az cli found at $pythonExe"
$pythonExe -m venv .temp/.env || fail

activate_python_venv
# TODO: Add support for automation testing in Linux Scripts.
python ./appliance_setup/run.py "$1" "$2" "${3:-INFO}" "${4:-false}"
operation_exit_code=$?
print_operation_status_message "$1" "$operation_exit_code"
deactivate_python_venv

exit "$operation_exit_code"
