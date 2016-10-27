<?php
$PINI_CONSOLE_MENU = 2;
include_once('./_common.php');

$result = array ('res'=>0);

$mb_id = $member["mb_id"];
$idx = mysql_real_escape_string($_POST["idx"]);

$row = sql_fetch("SELECT * FROM `pini_console`.`AOSSettings` WHERE `build_idx`='$idx' and `mb_id`='$mb_id' ");
if($row){
	$result["res"] = 1;
	$result["idx"] = $row["idx"];
	$result["gameName"] = $row["gameName"];
	$result["packageName"] = $row["packageName"];
	$result["appVersion"] = $row["appVersion"];
	$result["icon"] = $row["icon"];
	$result["keystore"] = false;
	if(strlen($row["keystore"]) > 0)
		$result["keystore"] = true;
	$result["apkpath"] = false;
	if(strlen($row["apkpath"]) > 0)
		$result["apkpath"] = true;
	$result["password"] = $row["password"];
}

echo json_encode($result);

?>