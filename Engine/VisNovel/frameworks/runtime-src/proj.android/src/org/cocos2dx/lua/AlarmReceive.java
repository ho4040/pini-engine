package org.cocos2dx.lua;

import com.nooslab.pini_remote_landscape.R;

import android.app.Notification;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.util.Log;
import android.content.Context;
import android.content.Intent;
import android.content.ComponentName;
import android.content.BroadcastReceiver;
import android.content.ServiceConnection;
import android.os.Bundle;
import android.os.IBinder;
import android.widget.Toast;
import android.app.AlarmManager;
import android.os.Vibrator;

import org.cocos2dx.lua.AppActivity;

public class AlarmReceive extends BroadcastReceiver {
	@Override
	public void onReceive(Context context, Intent intent) {
		try{
			// Toast.makeText(context, "Alarm Received!", Toast.LENGTH_LONG).show();
			NotificationManager notifier = (NotificationManager) context.getSystemService(Context.NOTIFICATION_SERVICE);
												//노티피케이션바에 나타낼 아이콘이미지
			Notification notify = new Notification(R.drawable.icon, intent.getExtras().getString("title"), System.currentTimeMillis());
			PendingIntent contentIntent = PendingIntent.getActivity(context, 0, new Intent(context, AppActivity.class)
											.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
											.putExtra("sendId", intent.getExtras().getString("name")),
										  PendingIntent.FLAG_UPDATE_CURRENT);
			notify.setLatestEventInfo(context, intent.getExtras().getString("title"),intent.getExtras().getString("text"),	contentIntent);
			notify.flags |= Notification.FLAG_AUTO_CANCEL;//노티피케이션에서 선택하면 표시를 없앨지 말지 설정
			//notify.vibrate = new long[] { 200, 200, 500, 300 };//진동 설정
			notify.number++;
			notifier.notify(1, notify);//노티를 던진다!
			
			Vibrator vibe = (Vibrator) context.getSystemService(Context.VIBRATOR_SERVICE);       
			vibe.vibrate(100);
			
		}catch(Exception e){
			// Toast.makeText(context, "e:"+e.toString(), Toast.LENGTH_LONG).show();
			// Log.e("recieve", e.toString());
		}
	}
}