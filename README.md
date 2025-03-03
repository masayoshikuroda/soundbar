# Sound Bar

Yamama YAS108用のbluetoothリモコン。

# 事前条件

- Phaton3
- bleak

# 使い側

## アドレスの取得

scan.pyでターゲットアドレスを取得
```
soundbar % python scan.py
--- 909D279B-325F-44A8-CA5D-8C63B6C941F6 ---
LOCAL_NAME :  YamahaAV
RSSI       :  -69
soundbar % 
```

## ステータスの取得

オプションなしで、soundbar.pyを実行
```
soundbar % python soundbar.py $ADDRESS                                                   
{
    "code": "ccaa0d05001107000900202000000a4043",
    "mute": false,
    "volume": 9,
    "subwoofer": "-4",
    "surround": "TV",
    "3d_sound": true,
    "clear_voice": false,
    "bass_ext": false
}
soundbar %  
```

## コマンドの実行

オプションを指定してsoundbar.pyを実行
```
soundbar % python soundbar.py $ADDRESS --surround movie --sound_3d on --clear_voice off --bass_ext on --volume down --subwoofer up
{
    "code": "ccaa0d0500110700080420200000036027",
    "mute": false,
    "volume": 8,
    "subwoofer": "-3",
    "surround": "MOVIE",
    "3d_sound": true,
    "clear_voice": false,
    "bass_ext": true
}
soundbar % 
```
# ブラウザ上での例

JavaScript上のWebBluetooth APIでのコマンド実行例

https://masayoshikuroda.github.io/soundbar/soundbar.html