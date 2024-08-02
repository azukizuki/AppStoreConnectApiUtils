自分用のAppStoreConnectAPIラッパーです。
ProvisioningProfile系のAPIとDevice系のAPIを中心に書いてますが今後メンテしてくかも。

# 使い方
AppStoreConnectApiWrapperにkeyId,IssuerId,p8ファイルへのパスを入れるだけで使えます。
現状は僕が必要だったものしか実装してません

# 現状の機能
- DeviceList取得
- ProfileList取得
- Profile情報取得
- 名前からProfileを検索して取得
- Profileに紐づくCertificatesの取得
- Profileに紐づくDevicesの取得
- Profileに紐づくBundleIdsの取得
- Deviceの追加
- Profile削除
- Profileの複製
- Profileに対して全てのデバイスを登録して更新する

# サンプル実装について
サンプルコードとして以下を入れています
- ProvisioningProfileをAppStoreConnectAPI経由でDLする
- FirebaseAppDistributionで手に入るTSVファイルを元に端末登録を行う
- 指定したProvisioningProfileに登録済み端末全てを登録し更新を行う

