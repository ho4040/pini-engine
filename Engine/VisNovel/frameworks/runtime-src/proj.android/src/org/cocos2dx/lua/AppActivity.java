/****************************************************************************
Copyright (c) 2008-2010 Ricardo Quesada
Copyright (c) 2010-2012 cocos2d-x.org
Copyright (c) 2011      Zynga Inc.
Copyright (c) 2013-2014 Chukong Technologies Inc.
 
http://www.cocos2d-x.org

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
****************************************************************************/
package org.cocos2dx.lua;

import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;

import org.cocos2dx.lib.Cocos2dxActivity;
import org.cocos2dx.lib.Cocos2dxLuaJavaBridge;
import org.json.JSONObject;

import android.provider.Settings;

import android.app.PendingIntent;
import android.content.ComponentName;
import android.content.DialogInterface;
import android.content.Context;
import android.content.Intent;
import android.content.ServiceConnection;
import android.content.BroadcastReceiver;
import android.app.ProgressDialog;

import android.app.AlertDialog;
import android.os.Bundle;
import android.os.IBinder;
import android.os.Vibrator;
import android.os.Messenger;
import android.util.Log;
import android.widget.Toast;
import android.app.AlarmManager;
import android.widget.RelativeLayout;
import android.net.Uri;
import android.net.wifi.WifiManager;
import android.net.NetworkInfo;
import android.net.ConnectivityManager;
import android.net.wifi.WifiInfo;
import android.net.wifi.WifiManager;

import com.adop.sdk.AdEntry;
import com.adop.sdk.BaseInterstitial;
import com.adop.sdk.OptimaAdListener;
import com.adop.sdk.BaseAdView;
import com.vungle.publisher.VunglePub;
import com.vungle.publisher.EventListener;

import android.content.pm.PackageManager.NameNotFoundException;
import com.google.android.vending.expansion.downloader.Helpers;
import com.google.android.vending.expansion.downloader.DownloaderClientMarshaller;

import android.util.AndroidException;
import com.google.android.vending.expansion.downloader.impl.DownloaderService;

import com.android.util.IabHelper;
import com.android.util.IabResult;
import com.android.util.Purchase;
import com.android.vending.billing.IInAppBillingService;

import android.content.pm.ActivityInfo;
import android.view.WindowManager;
import android.view.View;

import org.cocos2dx.lua.AlarmReceive;
import com.android.vending.expansion.zipfile.ZipResourceFile;
import com.android.vending.expansion.zipfile.ZipResourceFile.ZipEntryRO;
import com.google.android.vending.expansion.downloader.Constants;
import com.google.android.vending.expansion.downloader.DownloadProgressInfo;
import com.google.android.vending.expansion.downloader.DownloaderClientMarshaller;
import com.google.android.vending.expansion.downloader.DownloaderServiceMarshaller;
import com.google.android.vending.expansion.downloader.Helpers;
import com.google.android.vending.expansion.downloader.IDownloaderClient;
import com.google.android.vending.expansion.downloader.IDownloaderService;
import com.google.android.vending.expansion.downloader.IStub;

public class AppActivity extends Cocos2dxActivity implements IDownloaderClient{
    static AppActivity _this;
    IInAppBillingService mService;
    IabHelper mHelper = null;
    final VunglePub vunglePub = VunglePub.getInstance();

    public String PUBLIC_KEY = "";

    static String hostIPAdress = "0.0.0.0";
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
 
        bindService(new Intent("com.android.vending.billing.InAppBillingService.BIND"), mServiceConn, Context.BIND_AUTO_CREATE);
        AppActivity._this = this;

        if(nativeIsLandScape()) {
            setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_SENSOR_LANDSCAPE);
        } else {
            setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_SENSOR_PORTRAIT);
        }
        
        //2.Set the format of window
        
        // Check the wifi is opened when the native is debug.
        if(nativeIsDebug())
        {
            getWindow().setFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON, WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
            if(!isNetworkConnected())
            {
                AlertDialog.Builder builder=new AlertDialog.Builder(this);
                builder.setTitle("Warning");
                builder.setMessage("Please open WIFI for debuging...");
                builder.setPositiveButton("OK",new DialogInterface.OnClickListener() {
                    
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        startActivity(new Intent(Settings.ACTION_WIFI_SETTINGS));
                        finish();
                        System.exit(0);
                    }
                });

                builder.setNegativeButton("Cancel", null);
                builder.setCancelable(true);
                builder.show();
            }
            hostIPAdress = getHostIpAddress();
        }
    }

    //FOR EXTENSION FILE!
    private IStub mDownloaderClientStub;
    private IDownloaderService mRemoteService;
    private ProgressDialog mProgressDialog=null;
    ServiceConnection mServiceConn = new ServiceConnection() {
        @Override
        public void onServiceDisconnected(ComponentName name) {
            mService = null;
        }

        @Override
        public void onServiceConnected(ComponentName name, IBinder service) {
            mService = IInAppBillingService.Stub.asInterface(service);
        }
    };

    private void showOBBDownload(){
        Log.d("cocos2d-x","showOBBDownload>>>>>> show!");
        if(mProgressDialog == null){
            mProgressDialog = new ProgressDialog(this);
            mProgressDialog.setMessage("리소스파일을 다운로드합니다.");
            mProgressDialog.setProgressStyle(ProgressDialog.STYLE_HORIZONTAL);
            mProgressDialog.setCancelable(false);
            mProgressDialog.show();
        }
    }

    private void closeOBBDownload(){
        Log.d("cocos2d-x","closeOBBDownload>>>>>> close!");
        if(mProgressDialog != null){
            mProgressDialog.dismiss();
            mProgressDialog = null;
        }
    }

    private void updateOBBProgress(float now,float max){
        Log.d("cocos2d-x","updateOBBProgress>>>>>>"+Float.toString(now)+"/"+Float.toString(max));
        if(mProgressDialog == null){
            showOBBDownload();
        }
        mProgressDialog.setProgress((int)(now/max * 100));
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        if (mServiceConn != null) {
            unbindService(mServiceConn);
        }
    }

    @Override
    public void onPause() {
        super.onPause();
        vunglePub.onPause();
    }

    @Override
    public void onResume() {
        super.onResume();
        vunglePub.onResume();
    }

    @Override
    public void onServiceConnected(Messenger m){
        Log.d("cocos2d-x",">>>onServiceConnected");
        mRemoteService = DownloaderServiceMarshaller.CreateProxy(m);
        mRemoteService.onClientUpdated(mDownloaderClientStub.getMessenger());
    }
    @Override
    public void onDownloadStateChanged(int newState){
        Log.d("cocos2d-x",">>>onDownloadStateChanged : "+Integer.toString(newState));
        boolean showDialog;
        String ret = "";
        switch (newState) {
            case IDownloaderClient.STATE_IDLE:
                showDialog = false;
                break;
            case IDownloaderClient.STATE_CONNECTING:
            case IDownloaderClient.STATE_FETCHING_URL:
                showDialog = true;
                break;
            case IDownloaderClient.STATE_DOWNLOADING:
                showDialog = true;
                break;
            case IDownloaderClient.STATE_FAILED_CANCELED:
            case IDownloaderClient.STATE_FAILED:
            case IDownloaderClient.STATE_FAILED_FETCHING_URL:
            case IDownloaderClient.STATE_FAILED_UNLICENSED:
                ret = "0";
                showDialog = false;
                break;
            case IDownloaderClient.STATE_PAUSED_NEED_CELLULAR_PERMISSION:
            case IDownloaderClient.STATE_PAUSED_WIFI_DISABLED_NEED_CELLULAR_PERMISSION:
                ret = "0";
                showDialog = false;
                break;
            case IDownloaderClient.STATE_PAUSED_BY_REQUEST:
                showDialog = false;
                break;
            case IDownloaderClient.STATE_PAUSED_ROAMING:
            case IDownloaderClient.STATE_PAUSED_SDCARD_UNAVAILABLE:
                ret = "0";
                showDialog = false;
                break;
            case IDownloaderClient.STATE_COMPLETED:
                ret = "1";
                showDialog = false;
                break;
            default:
                showDialog = false;
        }

        if(showDialog){
            showOBBDownload();
        }else{
            closeOBBDownload();
        }
        if(ret.length() > 0){
            CallLua("PINI_OBB_DOWNLOAD_RESULT",ret);
        }
    }
    @Override
    public void onDownloadProgress(DownloadProgressInfo progress){
        Log.d("cocos2d-x",">>>onDownloadProgress");
        int total = (int)(progress.mOverallTotal >> 8);
        int now = (int)(progress.mOverallProgress >> 8);

        Log.d("cocos2d-x",Integer.toString(now) +" / "+ Integer.toString(total));

        updateOBBProgress((float)now,(float)total);
    }

    //한번에 모든 아이템 컨슘하는건 필요 음슴.. ㅠㅠ
    // public void AlreadyPurchaseItems() {
    //  try {
    //      Bundle ownedItems = mService.getPurchases(3, getPackageName(), "inapp", null);
    //      int response = ownedItems.getInt("RESPONSE_CODE");
    //      if (response == 0) {
    //          ArrayList purchaseDataList = ownedItems
    //                  .getStringArrayList("INAPP_PURCHASE_DATA_LIST");
    //          String[] tokens = new String[purchaseDataList.size()];
    //          for (int i = 0; i < purchaseDataList.size(); ++i) {
    //              String purchaseData = (String) purchaseDataList.get(i);
    //              JSONObject jo = new JSONObject(purchaseData);
    //              tokens[i] = jo.getString("purchaseToken");
    //              // 여기서 tokens를 모두 컨슘 해주기
    //              mService.consumePurchase(3, getPackageName(), tokens[i]);
    //          }
    //      }

    //      // 토큰을 모두 컨슘했으니 구매 메서드 처리
    //  } catch (Exception e) {
    //      e.printStackTrace();
    //  }
    // }

    public void _IAB_Settings(String hash){
        if(hash.length() == 0){
            hash = PUBLIC_KEY;
        }
        final String base64EncodedPublicKey = hash;//"MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEApGNrMQelP74XGKv5nJ87eZiKpv67+TvyiDyTkJrNBLLIFWlaoCyUuRlV44sb+LwmOQ08QVFIef14TNFWsSgKf28oLq/OcDgaWrs6L4WTVEW+WwOLjT5lFYufbpopgsNCt51H0to3nCVLT17En14VLcw41uxhpNPbydDdzgxXzhcnfQ9J3wmqO8GoGhN5PTD7RRMhjPzsE6gTYAO2GMtklGl2wc3Xn+QnhqKL0V29BfAtsWhQST1cMzX+PL1Z85n8QRHiLXqVn2nMO8LFZ/7lGSSl8jXAv06coqcY4aO5idv/I/tGFIRzE0bB82x3MlORlZx6zMzhjVC8v3pxN2MbewIDAQAB";

        mHelper = new IabHelper(this, base64EncodedPublicKey);
        mHelper.enableDebugLogging(true);
        mHelper.startSetup(new IabHelper.OnIabSetupFinishedListener() {
            public void onIabSetupFinished(IabResult result) {
                if (!result.isSuccess()) {
                    Toast.makeText(AppActivity.this, "can not init in-app-billing service",Toast.LENGTH_SHORT).show();
                    return;
                }
            }
        });
    }

    //구매메서드 입니다.
    public void _IAB_Buy(String id_item) {
        final String _id_item = id_item;
        // Var.ind_item = index;
        this.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                try {
                    Bundle buyIntentBundle = mService.getBuyIntent(3, getPackageName(), _id_item, "inapp", "test");
                    PendingIntent pendingIntent = buyIntentBundle.getParcelable("BUY_INTENT");

                    if (pendingIntent != null) {
                        mHelper.launchPurchaseFlow(AppActivity.this, getPackageName(), 1001,  mPurchaseFinishedListener, "test");
                    } else {
                        JSONObject result = new JSONObject();
                        try {
                            result.put("result",false);
                        }catch (Exception e) {
                            Toast.makeText(AppActivity.this, "JSON ERROR!",Toast.LENGTH_SHORT).show();
                        }
                        CallLua("PINI_IAP_CALLBACK", result.toString());
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        });
    }

    public void _IAB_Check(final String id_item){
        this.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                try {
                    Bundle ownedItems = mService.getPurchases(3, getPackageName(), "inapp", null);
                    int response = ownedItems.getInt("RESPONSE_CODE");
                    JSONObject result = new JSONObject();
                    if (response == 0) {
                        ArrayList purchaseDataList = ownedItems.getStringArrayList("INAPP_PURCHASE_DATA_LIST");
                        for (int i = 0; i < purchaseDataList.size(); ++i) {
                            String purchaseData = (String) purchaseDataList.get(i);
                            JSONObject jo = new JSONObject(purchaseData);
                            if(jo.getString("productId").equals(id_item)){
                                result.put("result",1);
                                CallLua("PINI_IAP_CHECK_CALLBACK", result.toString());
                                return ;
                            }
                        }
                        result.put("result",0);
                        CallLua("PINI_IAP_CHECK_CALLBACK", result.toString());
                        return ;
                    }
                    result.put("result",0);
                    CallLua("PINI_IAP_CHECK_CALLBACK", result.toString());
                    return ;
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        });
    }

    public void _IAB_Consume(final String id_item){
        this.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                try {
                    Bundle ownedItems = mService.getPurchases(3, getPackageName(), "inapp", null);
                    int response = ownedItems.getInt("RESPONSE_CODE");
                    JSONObject result = new JSONObject();
                    if (response == 0) {
                        ArrayList purchaseDataList = ownedItems.getStringArrayList("INAPP_PURCHASE_DATA_LIST");
                        for (int i = 0; i < purchaseDataList.size(); ++i) {
                            String purchaseData = (String) purchaseDataList.get(i);
                            JSONObject jo = new JSONObject(purchaseData);
                            String token = jo.getString("purchaseToken");
                            if(jo.getString("productId").equals(id_item)){
                                mService.consumePurchase(3, getPackageName(), token);
                                
                                result.put("result",1);
                                CallLua("PINI_IAP_CONSUME_CALLBACK", result.toString());
                                return ;
                            }
                        }
                        result.put("result",0);
                        CallLua("PINI_IAP_CONSUME_CALLBACK", result.toString());
                        return ;
                    }
                    result.put("result",0);
                    CallLua("PINI_IAP_CONSUME_CALLBACK", result.toString());
                    return ;
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        });
    }

    public void _Toast(final String str,final int time){
        this.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                try {
                    Toast.makeText(AppActivity.this, str, time).show();
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        });
    } 


    public void _ADS_Banner(){
        this.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                try {
                    // BaseAdView mAdView = new BaseAdView(AppActivity.this);
                    // AdEntry aEntry = new AdEntry("342");
                    // mAdView.setAdInfo(aEntry, AppActivity.this);
                    // mAdView.load();
                    
                    // RelativeLayout.LayoutParams params = new RelativeLayout.LayoutParams(
                    //         RelativeLayout.LayoutParams.MATCH_PARENT, RelativeLayout.LayoutParams.WRAP_CONTENT);
                    // mFrameLayout.addView(mAdView, params);
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        });
    }       

    public void _ADS_Fullscreen(){
        this.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                try {
                    BaseInterstitial interstitialAd = new BaseInterstitial(AppActivity.this); // 전면 광고 설정
                    AdEntry info = new AdEntry("357"); // ZoneID 입력
                    interstitialAd.setAdInfo(info, AppActivity.this); // 광고정보 설정
                    interstitialAd.load(); // 광고 로드 및 show
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        });
    }

    public void _Vibrator(final long ms){
        this.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                try {
                    //Log.d("cocos2d-x",ms.toString());
                    Vibrator vibe = (Vibrator) getSystemService(Context.VIBRATOR_SERVICE);       
                    vibe.vibrate(ms);
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        });
    }

    public void _localPush(final String title,final String text,final int vibrate,final int day,final int hour,final int min,final int sec){
        this.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                try{
                    // Toast.makeText(AppActivity.this, day+" : ready",Toast.LENGTH_LONG).show();

                     // get a Calendar object with current time
                    Calendar cal = Calendar.getInstance();
                    // add 5 minutes to the calendar object
                    cal.add(Calendar.DATE, day);
                    cal.add(Calendar.HOUR_OF_DAY, hour);
                    cal.add(Calendar.MINUTE, min);
                    cal.add(Calendar.SECOND, sec);
                    Intent intent = new Intent(AppActivity.this, AlarmReceive.class);
                    intent.putExtra("title", title);
                    intent.putExtra("text", text);
                    intent.putExtra("vibrate", vibrate);

                    // In reality, you would want to have a static variable for the request code instead of 192837
                    PendingIntent sender = PendingIntent.getBroadcast(AppActivity.this, 192837, intent, PendingIntent.FLAG_UPDATE_CURRENT);

                    // Get the AlarmManager service
                    AlarmManager am = (AlarmManager) getSystemService(ALARM_SERVICE);
                    am.set(AlarmManager.RTC_WAKEUP, cal.getTimeInMillis(), sender);

                }catch(Exception e){
                    e.printStackTrace();
                }
            }
        });
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode,resultCode,data);

        if(mHelper != null){
            JSONObject result = new JSONObject();
            try {
                if (!mHelper.handleActivityResult(requestCode, resultCode, data)) {
                    super.onActivityResult(requestCode, resultCode, data);
                }
                
                result.put("result",false);
                if(requestCode == 1001){
                    if (resultCode == RESULT_OK) {
                    }else{
                        CallLua("PINI_IAP_CALLBACK", result.toString());
                    }
                }else{
                    CallLua("PINI_IAP_CALLBACK", result.toString());
                }
            } catch (Exception e) {
                Toast.makeText(AppActivity.this, "JSON ERROR!",Toast.LENGTH_SHORT).show();
            }
        }
    }

    IabHelper.OnIabPurchaseFinishedListener mPurchaseFinishedListener  = new IabHelper.OnIabPurchaseFinishedListener() {
       public void onIabPurchaseFinished(IabResult iabResult, Purchase purchase) 
       {
            JSONObject result = new JSONObject();
            try {
                    if(iabResult.isSuccess()){
                        String purchaseData = purchase.getOriginalJson();
                        String dataSignature = purchase.getSignature();

                        result.put("result",true);
                        result.put("purchaseData",purchaseData);
                        result.put("dataSignature",dataSignature);

                        CallLua("PINI_IAP_CALLBACK", result.toString());

                        //AlreadyPurchaseItems();
                    }else{
                        CallLua("PINI_IAP_CALLBACK", result.toString());
                    }
            } catch (Exception e) {
                Toast.makeText(AppActivity.this, "JSON ERROR!",Toast.LENGTH_SHORT).show();
            }
       }
    };

    public boolean _ExtensionFile_IsFileExists(String type,String versionCode,int size){
        String mainFileName = type + "." + versionCode + "." + getPackageName() + ".obb";
        return Helpers.doesFileExist(this, mainFileName, size , false);
    }

    public void _ExtensionFile_Download(){
        Log.d("cocos2d-x", "_ExtensionFile_Download 1");
        this.runOnUiThread(new Runnable() {
            @Override
            public void run() {
            Log.d("cocos2d-x", "_ExtensionFile_Download 2");
                try{
            Log.d("cocos2d-x", "_ExtensionFile_Download -1");
                    Intent launcher = getIntent();
                    Intent fromNotification = new Intent(AppActivity._this, getClass());
            Log.d("cocos2d-x", "_ExtensionFile_Download -2");
                    fromNotification.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
                    fromNotification.setAction(launcher.getAction());
            Log.d("cocos2d-x", "_ExtensionFile_Download -3");
                    if (launcher.getCategories() != null) {
            Log.d("cocos2d-x", "_ExtensionFile_Download -4");
                        for (String cat : launcher.getCategories()) {
                            fromNotification.addCategory(cat);
            Log.d("cocos2d-x", "_ExtensionFile_Download -5");
                        }
            Log.d("cocos2d-x", "_ExtensionFile_Download -6");
                    }
                    PendingIntent pendingIntent = PendingIntent.getActivity(AppActivity._this, 0, fromNotification, PendingIntent.FLAG_UPDATE_CURRENT);
            Log.d("cocos2d-x", "_ExtensionFile_Download -7");
                    try {
                        // Start the download
            Log.d("cocos2d-x", "_ExtensionFile_Download -8");
                        int result = DownloaderClientMarshaller.startDownloadServiceIfRequired(AppActivity._this, pendingIntent, ExpansionFileDownloaderService.class);
            Log.d("cocos2d-x", "_ExtensionFile_Download -9");
                        if (DownloaderClientMarshaller.NO_DOWNLOAD_REQUIRED != result) {
                            if( result == DownloaderClientMarshaller.LVL_CHECK_REQUIRED ){
            Log.d("cocos2d-x", "_ExtensionFile_Download -10");
                                AlertDialog.Builder alert = new AlertDialog.Builder(AppActivity._this);
                                alert.setMessage("Cannot access lisense checker. please use 'com.android.vending.CHECK_LICENSE' permission flag.");
                                alert.show();

            Log.d("cocos2d-x", "_ExtensionFile_Download -11");
                                CallLua("PINI_OBB_DOWNLOAD_RESULT","-1");
                                return;
                            }
            Log.d("cocos2d-x", "_ExtensionFile_Download -12");
                            mDownloaderClientStub = DownloaderClientMarshaller.CreateStub(AppActivity._this,ExpansionFileDownloaderService.class);
                            mDownloaderClientStub.connect(AppActivity._this);
                            return;
                        }
                    } catch (NameNotFoundException e) {
                        Log.d("cocos2d-x", "NameNotFoundException occurred. " + e.getMessage(), e);
                    }
                    CallLua("PINI_OBB_DOWNLOAD_RESULT","-2");
                } catch (Exception e) {
                    Log.d("cocos2d-x", "_ExtensionFile_Download exception");
                    e.printStackTrace();
                }
            }
        });
        Log.d("cocos2d-x", "_ExtensionFile_Download 3");
    }

    public void _VungleInit(final String appId){
        this.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                try{
                    vunglePub.init(AppActivity.this, appId);
                    vunglePub.setEventListeners(new EventListener(){
                        @Override
                        public void onVideoView(
                            boolean isCompletedView, int watchedMillis, int videoDurationMillis) {
                            CallLua("LNX_VUNGLE_CALLBACK","" + videoDurationMillis);
                        }

                        @Override
                        public void onAdStart() {
                            // Called before playing an ad.
                        }

                        @Override
                        public void onAdUnavailable(String reason) {
                            // Called when VunglePub.playAd() was called but no ad is available to show to the user.
                        }

                        @Override
                        public void onAdEnd(boolean wasCallToActionClicked) {
                            // Called when the user leaves the ad and control is returned to your application.
                        }

                        @Override
                        public void onAdPlayableChanged(boolean isAdPlayable) {
                            // Called when ad playability changes.
                        }
                    });
                }catch(Exception e){
                    e.printStackTrace();
                }
            }
        });
    }

    public void _VunglePlay(){
        this.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                try{
                    vunglePub.playAd();
                }catch(Exception e){
                    e.printStackTrace();
                }
            }
        });
    }

    public void CallLua(final String funcName,final String arg){
        this.runOnGLThread(new Runnable() {
            @Override
            public void run() {
                try{
                    Cocos2dxLuaJavaBridge.callLuaGlobalFunctionWithString(funcName, arg);
                }catch(Exception e){
                    e.printStackTrace();
                }
            }
        });
    }

    //////////////////////////////////////////////////////
    //브릿지용 static 함수들
    public static void IAB_Settings(String hash){
        AppActivity._this._IAB_Settings(hash);
    }
    public static void IAB_Buy(String id_item){
        AppActivity._this._IAB_Buy(id_item);
    }
    public static void IAB_Consume(String id){
        AppActivity._this._IAB_Consume(id);
    }
    public static void IAB_Check(String id_item){
        AppActivity._this._IAB_Check(id_item);
    }
    public static void Android_Toast(String str,float time){
        AppActivity._this._Toast(str,(int)time);
    }
    public static void ADS_Fullscreen(){
        AppActivity._this._ADS_Fullscreen();
    }
    public static void ADS_Banner(){
        AppActivity._this._ADS_Banner();
    }
    public static void Device_LocalPush(String title,String text,float vibrate,float day,float hour, float min, float sec){
        AppActivity._this._localPush(title,text,(int)vibrate,(int)day,(int)hour,(int)min,(int)sec);
    }
    public static void Device_Vibrator(float ms){
        AppActivity._this._Vibrator((long)ms);
    }
    public static boolean ExtensionFile_IsFileExists(String type,String versionCode,String size){
        return AppActivity._this._ExtensionFile_IsFileExists(type,versionCode,Integer.parseInt(size));
    }
    public static void ExtensionFile_Download(){
        AppActivity._this._ExtensionFile_Download();
    }
    public static void Extension_SetPublicKey(String pkey){
        AppActivity._this.PUBLIC_KEY = pkey;
    }
    public static String AppPackageName(){
        return AppActivity._this.getPackageName();
    }
    public static String OBBDirPath(){
        return Helpers.getSaveFilePath(AppActivity._this);
    }
    public static void VungleInit(String appId){
        AppActivity._this._VungleInit(appId);
    }
    public static void VunglePlay(){
        AppActivity._this._VunglePlay();
    }

    public static void HideSoftKey(){
        View decorView = AppActivity._this.getWindow().getDecorView();
		int uiOptions = View.SYSTEM_UI_FLAG_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_FULLSCREEN;
		decorView.setSystemUiVisibility(uiOptions);
    }

    
    //////////////////////////////////////////////////////
    
    @Override
    protected void onStop() {
        if (null != mDownloaderClientStub) {
            mDownloaderClientStub.disconnect(this);
        }
        super.onStop();
    }

    /**
     * Connect the stub to our service on start.
     */
    @Override
    protected void onStart() {
        if (null != mDownloaderClientStub) {
            mDownloaderClientStub.connect(this);
        }
        super.onStart();
    }

    private boolean isNetworkConnected() {
            ConnectivityManager cm = (ConnectivityManager) getSystemService(Context.CONNECTIVITY_SERVICE);  
            if (cm != null) {  
                NetworkInfo networkInfo = cm.getActiveNetworkInfo();  
            ArrayList networkTypes = new ArrayList();
            networkTypes.add(ConnectivityManager.TYPE_WIFI);
            try {
                networkTypes.add(ConnectivityManager.class.getDeclaredField("TYPE_ETHERNET").getInt(null));
            } catch (NoSuchFieldException nsfe) {
            }
            catch (IllegalAccessException iae) {
                throw new RuntimeException(iae);
            }
            if (networkInfo != null && networkTypes.contains(networkInfo.getType())) {
                    return true;  
                }  
            }  
            return false;  
        } 
     
    public String getHostIpAddress() {
        WifiManager wifiMgr = (WifiManager) getSystemService(WIFI_SERVICE);
        WifiInfo wifiInfo = wifiMgr.getConnectionInfo();
        int ip = wifiInfo.getIpAddress();
        return ((ip & 0xFF) + "." + ((ip >>>= 8) & 0xFF) + "." + ((ip >>>= 8) & 0xFF) + "." + ((ip >>>= 8) & 0xFF));
    }
    
    public static String getLocalIpAddress() {
        return hostIPAdress;
    }
    
    private static native boolean nativeIsLandScape();
    private static native boolean nativeIsDebug();
    
    static {
        System.loadLibrary("avutil-52");
        System.loadLibrary("avcodec-55");
        System.loadLibrary("avformat-55");
        System.loadLibrary("swresample-0");
        System.loadLibrary("swscale-2");
        System.loadLibrary("openal");
    }
}