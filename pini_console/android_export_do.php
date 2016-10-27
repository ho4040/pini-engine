<?php
$PINI_CONSOLE_MENU = 2;
include_once('./_common.php');

$result = array ('res'=>0);

$mb_id = $member["mb_id"];
$idx = mysql_real_escape_string($_POST["idx"]);

function uploadfile($port,$page,$filename){
	$url = 'http://nooslab.iptime.org:'.$port.'/'.$page;
	$header = array('Content-Type: multipart/form-data');
	$fields = array('file' => '@' . $filename);
	 
	$resource = curl_init();
	curl_setopt($resource, CURLOPT_URL, $url);
	curl_setopt($resource, CURLOPT_HTTPHEADER, $header);
	curl_setopt($resource, CURLOPT_RETURNTRANSFER, 1);
	curl_setopt($resource, CURLOPT_POST, 1);
	curl_setopt($resource, CURLOPT_POSTFIELDS, $fields);
	$result = json_decode(curl_exec($resource),true);
	curl_close($resource);
	return $result;
}

function post($port,$page,$arg){
	$url = 'http://nooslab.iptime.org:'.$port.'/'.$page;
	$fields = $arg;
	 
	$resource = curl_init();
	curl_setopt($resource, CURLOPT_URL, $url);
	curl_setopt($resource, CURLOPT_RETURNTRANSFER, 1);
	curl_setopt($resource, CURLOPT_POST, 1);
	curl_setopt($resource, CURLOPT_HTTPHEADER, 0);
	curl_setopt($resource, CURLOPT_POSTFIELDS, http_build_query($fields) );
	$result = json_decode(curl_exec($resource),true);
	curl_close($resource);
	return $result;
}

function download($port,$file,$dist){
	$url = 'http://nooslab.iptime.org:'.$port.'/requestFile?f='.$file;
	file_put_contents($dist, file_get_contents($url));
}

$row1 = sql_fetch("SELECT * FROM `pini_console`.`AOSSettings` WHERE `build_idx`='$idx' and `mb_id`='$mb_id' ");
$row2 = sql_fetch("SELECT * FROM `pini_console`.`builds`	  WHERE `idx`='$idx' and `mb_id`='$mb_id' ");

if($row1 && $row2){
	$result["res"] = true;
	$b1	= strlen($row1["gameName"]) > 0 ? true : false;
	$b2	= strlen($row1["packageName"]) > 5 ? true : false;
	$b3	= strlen($row1["appVersion"]) > 3 ? true : false;
	$b4	= strlen($row1["keystore"]) > 0 ? true : false;
	$b5	= strlen($row1["password"]) > 8 ? true : false;
	$b6	= strlen($row1["icon"]) > 0 ? true : false;
	
	$result["res"] = $b1 && $b2 && $b3 && $b5 && $b6;
	if($result["res"]){
		if($b4){
			$ret = uploadfile(9977,"uploadKeystore",$row1["keystore"]);
			$result["keystore"] = $ret;
		}
		$ret = uploadfile(9977,"uploadBuild",$row2["filename"]);
		$result["build"] = $ret;
		
		$ret = uploadfile(9977,"uploadIcon",$row1["icon"]);
		$result["icon"] = $ret;

		$ret = post(9977,"AndroidBuild",array('data' => $row1,'filename' => $row2["filename"]));
		$result["b"] = $ret["res"];

		if($ret["genKey"]){
			download(9977,$ret["key"],$ret["key"]);
			sql_fetch("UPDATE `pini_console`.`AOSSettings` SET `keystore` = '".$ret["key"]."' WHERE `build_idx`='$idx' and `mb_id`='$mb_id';");
		}

		download(9977,$ret["apk"],$ret["apk"]);
		sql_fetch("UPDATE `pini_console`.`AOSSettings` SET `apkpath` = '".$ret["apk"]."' WHERE `build_idx`='$idx' and `mb_id`='$mb_id';");
	}
}
echo json_encode($result);

?>