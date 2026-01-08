## Installing on Windows

Open a `git bash` terminal as admin.

```bash
mkdir tmp && cd tmp
```

### install zstd unpacker for tar

```bash
curl -L https://github.com/facebook/zstd/releases/download/v1.5.5/zstd-v1.5.5-win64.zip --output xxx
unzip xxx
cp zstd-v1.5.5-win64/zstd.exe  'c:\Program Files\Git\usr\bin\'
rm -r * .*
```

### install rsync

**Note**: You will need to get the latest binary paths from https://repo.msys2.org/msys/x86_64/.

```bash
curl -L https://repo.msys2.org/msys/x86_64/rsync-3.4.1-1-x86_64.pkg.tar.zst     --output xxx
tar -I zstd -xvf xxx
cp usr/bin/rsync.exe 'c:\Program Files\Git\usr\bin\'
rm -r * .*

curl -L https://repo.msys2.org/msys/x86_64/libzstd-1.5.7-1-x86_64.pkg.tar.zst  --output xxx
tar -I zstd -xvf xxx
cp usr/bin/msys-zstd-1.dll 'c:\Program Files\Git\usr\bin\'
rm -r * .*

curl -L https://repo.msys2.org/msys/x86_64/libxxhash-0.8.3-1-x86_64.pkg.tar.zst --output xxx
tar -I zstd -xvf xxx
cp usr/bin/msys-xxhash-0.dll 'c:\Program Files\Git\usr\bin\'
rm -r * .*

curl -L https://repo.msys2.org/msys/x86_64/liblz4-1.9.4-1-x86_64.pkg.tar.zst --output xxx
tar -I zstd -xvf xxx
cp usr/bin/msys-lz4-1.dll 'c:\Program Files\Git\usr\bin\'
rm -r * .*

curl -L https://repo.msys2.org/msys/x86_64/libopenssl-3.6.0-1-x86_64.pkg.tar.zst --output xxx
tar -I zstd -xvf xxx
cp usr/bin/msys-crypto-3.dll 'c:\Program Files\Git\usr\bin\'
rm -r * .*
```

### cleanup

```bash
cd .. && rm -r tmp
```
