// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Script} from "forge-std/Script.sol";
import {ProntuarioUnificado} from "../src/Prontuario.sol";

contract CounterScript is Script {
    ProntuarioUnificado public prontuario;

    function setUp() public {}

    function run() public {
        vm.startBroadcast();

        prontuario = new ProntuarioUnificado();

        vm.stopBroadcast();
    }
}
