// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {Script} from "forge-std/Script.sol";
import {ProntuarioUnificado} from "../src/Prontuario.sol";

contract DeployScript is Script {
    ProntuarioUnificado public prontuario;

    function run() external {
        vm.startBroadcast();
        prontuario = new ProntuarioUnificado();
        vm.stopBroadcast();
    }
}
