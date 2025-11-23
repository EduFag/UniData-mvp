// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import {Script} from "forge-std/Script.sol";
import {Unidata} from "../src/Unidata.sol";

contract DeployScript is Script {
    Unidata public unidata;

    function run() external {
        vm.startBroadcast();
        unidata = new Unidata();
        vm.stopBroadcast();
    }
}
