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

import com.android.util.IabHelper;
import com.android.util.IabResult;
import com.android.util.Purchase;
import com.android.vending.billing.IInAppBillingService;

public class ExpansionFileDownloaderService extends DownloaderService {
	private static final byte[] SALT = new byte[] {1, 42, -12, -1, 54, 98, -100, -12, 43, 2, -8, -4, 9, 5, -106, -107, -33, 45, -1, 84};

	@Override public String getPublicKey() {
		return AppActivity._this.PUBLIC_KEY;
	}
	@Override public byte[] getSALT() {
		return SALT;
	}
	@Override public String getAlarmReceiverClassName() {
		return ExpansionFileAlarmReceiver.class.getName();
	}
}
