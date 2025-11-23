// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Script} from "forge-std/Script.sol";
import {Unidata} from "../src/Unidata.sol";

contract CounterScript is Script {
    Unidata public unidata;

    function setUp() public {}

    function run() public {
        vm.startBroadcast();

        unidata = new Unidata();

        vm.stopBroadcast();
    }
}
