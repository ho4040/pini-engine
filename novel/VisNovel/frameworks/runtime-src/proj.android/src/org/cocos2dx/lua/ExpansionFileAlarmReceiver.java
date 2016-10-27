package org.cocos2dx.lua;

import java.util.ArrayList;
import java.util.Calendar;
import java.util.Date;

import org.cocos2dx.lib.Cocos2dxActivity;
import org.cocos2dx.lib.Cocos2dxLuaJavaBridge;
import org.json.JSONObject;

import android.app.PendingIntent;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.ServiceConnection;
import android.content.BroadcastReceiver;

import android.os.Bundle;
import android.os.IBinder;
import android.os.Vibrator;
import android.util.Log;
import android.widget.Toast;
import android.app.AlarmManager;
import android.widget.RelativeLayout;
import android.net.Uri;

import com.adop.sdk.AdEntry;
import com.adop.sdk.BaseInterstitial;
import com.adop.sdk.OptimaAdListener;
import com.adop.sdk.BaseAdView;

import android.content.pm.PackageManager.NameNotFoundException;
import com.google.android.vending.expansion.downloader.Helpers;
import com.google.android.vending.expansion.downloader.DownloaderClientMarshaller;

import android.util.AndroidException;
import com.google.android.vending.expansion.downloader.impl.DownloaderService;

public class ExpansionFileAlarmReceiver extends BroadcastReceiver {
	@Override public void onReceive(Context context, Intent intent) {
		try {
			Log.d("cocos2d-x"," >>>>> ExpansionFileAlarmReceiver >>>>> ");
			DownloaderClientMarshaller.startDownloadServiceIfRequired(context, intent, ExpansionFileDownloaderService.class);
		} catch (NameNotFoundException e) {
			Log.e("apk-expansion-files", "NameNotFoundException occurred. " + e.getMessage(), e);
		}
	}
}