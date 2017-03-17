<?php
$PINI_CONSOLE_MENU = 2;
include_once('./_common.php');

$result = array ('res'=>0);
$result["icon"] = false;

$mb_id = $member["mb_id"];
$idx = mysql_real_escape_string($_POST["AOS_idx"]);
$gameName = mysql_real_escape_string($_POST["AOS_gameName"]);
$packageName = mysql_real_escape_string($_POST["AOS_packageName"]);
$appVersion = mysql_real_escape_string($_POST["AOS_appVersion"]);
$keyPassword = mysql_real_escape_string($_POST["AOS_keyPassword"]);

$row = sql_fetch("SELECT * FROM `pini_console`.`AOSSettings` WHERE `build_idx`='$idx'");

$keystorefile = "";
$iconfile = "";
if($_FILES['AOS_keystore']){
	$uploaddir  = './upload/keystore/';
	$keystorefile = $uploaddir . md5(basename($_FILES['AOS_keystore']['name']).time());

	$count = 0;
	$tmp = $keystorefile;
	while(1){
		$msg .= $tmp;
		if(file_exists( $tmp.".key" )){
			$tmp = $keystorefile.$count;
			$count++;
		}else{
			break;
		}
	}
	$keystorefile = $tmp.".key";
	if(!move_uploaded_file($_FILES['AOS_keystore']['tmp_name'], $keystorefile)){
		$keystorefile = "";
	}
}
if($_FILES['AOS_icon']){
	$iconInfo = getimagesize($_FILES['AOS_icon']['tmp_name']);
	$result["icon"] = true;
	$result["iconW"] = $iconInfo[0];
	$result["iconH"] = $iconInfo[1];
	$result["iconT"] = $iconInfo[2];
	$result["iconA"] = $iconInfo[3];

	if($result["iconT"] == 3 && $result["iconW"] == 512 && $result["iconH"] == 512) {
		$uploaddir  = './upload/icon/';
		$iconfile = $uploaddir . md5(basename($_FILES['AOS_icon']['name']).time());

		$count = 0;
		$tmp = $iconfile;
		while(1){
			$msg .= $tmp;
			if(file_exists( $tmp.".png" )){
				$tmp = $iconfile.$count;
				$count++;
			}else{
				break;
			}
		}
		$iconfile = $tmp.".png";
		if(!move_uploaded_file($_FILES['AOS_icon']['tmp_name'], $iconfile)){
			$iconfile = "";
		}
	}
}


if($row){
	if($row["mb_id"] == $mb_id){
		if($keystorefile == ""){
			$keystorefile = $row["keystore"];
		}
		if($iconfile == ""){
			$iconfile = $row["icon"];
		}
		sql_fetch("UPDATE `pini_console`.`AOSSettings` SET 
						  `gameName` = '$gameName', 
						  `packageName` = '$packageName', 
						  `appVersion` = '$appVersion', 
						  `keystore` = '$keystorefile', 
						  `icon` = '$iconfile', 
						  `password` = '$keyPassword' 
					WHERE `build_idx`='$idx' and `mb_id`='$mb_id' ");
	}
}else{
	sql_fetch("INSERT INTO `pini_console`.`AOSSettings`
		(`idx`, `mb_id`, `build_idx`, `gameName`, `packageName`, `appVersion`, `keystore`, `icon`, `password`, `datetime`) VALUES
		(NULL, '$mb_id', '$idx', '$gameName', '$packageName', '$appVersion', '$keystorefile','$iconfile', '$keyPassword', CURRENT_TIMESTAMP);");
}
echo json_encode($result);
?>