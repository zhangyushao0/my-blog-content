---
date: 2023-5-24
title: Qemu debug with gdb in vscode
summary: The document provides a step-by-step guide on how to debug TF-M (Trusted Firmware-M) using QEMU and GDB in Visual Studio Code on Ubuntu 20.04. 
---
# Qemu debug with gdb in vscode

Environment: ubuntu 20.04, qemu 6.2.0, arm-none-eabi-gdb 12.1

## **Step1** : build TF-M with debug info

I follow part of the guide [TF-M debug with gdb], it said

>NOTE: If you are debugging, make sure to set the build type variable to `-DCMAKE_BUILD_TYPE=Debug` when building TF-M so that debug information is available to GDB.
>
>NOTE: When debugging with the mbed-crypto library, it is needed to add an additional `-DMBEDCRYPTO_BUILD_TYPE=DEBUG` compile-time switch.

So we should build TF-M as follows.

```bash
cd trusted-firmware-m
cmake -S . -B cmake_build -DTFM_PLATFORM=arm/mps2/an521 -DTFM_TOOLCHAIN_FILE=toolchain_GNUARM.cmake -DTEST_NS=ON -DTEST_S=ON -DTFM_PSA_API=ON -DBL2=OFF -DCMAKE_BUILD_TYPE=Debug -DMBEDCRYPTO_BUILD_TYPE=DEBUG
cd cmake_build
make
```

you can find the binary file in camke_build/bin.

## **Step 2** : install arm-none-eabi-gdb

I have tried install with

```bash
sudo apt install gdb-arm-none-eabi
```

But it seems no work for me, if yours cannot work too, you can try the method as follows from [how to install gdb-arm-none-eabi].

```bash
sudo apt install gdb-multiarch
```

## **Step3** : load the binary file into qemu in gdb debug mode without BL2

I follow part of the guide [qemu gdb], it said

>In order to use gdb, launch QEMU with the -s and -S options. The -s option will make QEMU listen for an incoming connection from gdb on TCP port 1234, and -S will make QEMU not start the guest until you tell it to from gdb.

and follow the instruction in [qemu loader], 

><div class="section" id="loading-files">
><h2>Loading Files</a></h2>
><p>The loader device also allows files to be loaded into memory. It can load ELF,U-Boot, and Intel HEX executable formats as well as raw images.  The syntax isshown below:</p>
><blockquote>
><div><p>-device loader,file=&lt;file&gt;[,addr=&lt;addr&gt;][,cpu-num=&lt;cpu-num&gt;][,force-raw=&lt;raw&gt;]</p>
></div></blockquote>
><dl class="simple">
><dt><code class="docutils literal notranslate"><span class="pre">&lt;file&gt;</span></code></dt><dd><p>A file to be loaded into memory</p>
></dd>
><dt><code class="docutils literal notranslate"><span class="pre">&lt;addr&gt;</span></code></dt><dd><p>The memory address where the file should be loaded. This is requiredfor raw images and ignored for non-raw files.</p>
></dd>
><dt><code class="docutils literal notranslate"><span class="pre">&lt;cpu-num&gt;</span></code></dt><dd><p>This specifies the CPU that should be used. This is anoptional argument and will cause the CPU’s PC to be set to the memory address where the raw file is loaded or the entry point specified in the executable format header. This option should only be used for the boot image. This will also cause the image to be written to the specified CPU’s address space. If not specified, the default is CPU 0.></p>


So we should run qemu as follows.

```bash
cd trusted-firmware-m/cmake_build/bin
qemu-system-arm -M mps2-an521 -device loader,file="tfm_ns.elf",addr=0x10056c -device loader,file="tfm_s.elf",addr=0x10009e18,cpu-num=0 -serial stdio -display none -s -S
```

## **Step4** : connect gdb to qemu in vscode

See the [qemu gdb], we can konw that qemu is running at the gdbserver in localhost:1234. So, you can actually debug in console with gdb now as follws.

```bash
cd trusted-firmware-m/cmake_build/bin
arm-none-eabi-gdb -tui tfm_s.elf
(gdb) target remote localhost:1234
```

If you want to debug in vscode, you should create the `.vsode` folder  and `launch.json` in it in the workspace. The content of `launch.json` is as follows.

```json
{
    "configurations": [
    {
        "name": "(gdb) 启动",
        "type": "cppdbg",
        "request": "launch",
        "program": "${workspaceFolder}/cmake_build/bin/tfm_s.elf",
        "args": [],
        "stopAtEntry": true,
        "cwd": "${fileDirname}",
        "environment": [],
        "externalConsole": false,
        "MIMode": "gdb",
        "miDebuggerPath": "/usr/bin/arm-none-eabi-gdb",
        "miDebuggerServerAddress": ":1234",
        "setupCommands": [
            {
                "description": "为 gdb 启用整齐打印",
                "text": "-enable-pretty-printing",
                "ignoreFailures": true
            },
            {
                "description": "载入非安全区符号表",
                "text": "add-symbol-file ${workspaceFolder}/cmake_build/bin/tfm_ns.elf 0x10056c",
                "ignoreFailures": false
            }
        ]
    }
    ]
}
```

If you don't use the wsl, you should connect to you virtual machines with ssh first in vscode.

Or you can gdb in local with the use of gdbserver. That is, you use the gdb connect to the vm. First of all, install arm-none-eabi-gdb in your local. Then pull the trusted-firmware-m to your local. Set it to be your workspace in vscode. Modify the `launch.json` as follows.

```json
"miDebuggerServerAddress": "[here to change]:1234",//you should change it to your vm's ip
```

Then you can debug in vscode now. But you'd better set a breakpoint in beginning of main() first.

[TF-M debug with gdb]: <https://tf-m-user-guide.trustedfirmware.org/platform/nxp/lpcxpresso55s69/README.html>

[how to install gdb-arm-none-eabi]: <https://askubuntu.com/questions/1031103/how-can-i-install-gdb-arm-none-eabi-on-ubuntu-18-04-bionic-beaver>

[qemu gdb]: <https://www.qemu.org/docs/master/system/gdb.html>

[qemu loader]: <https://qemu-project.gitlab.io/qemu/system/generic-loader.html>
