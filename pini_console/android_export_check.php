<?php
$PINI_CONSOLE_MENU = 2;
include_once('./_common.php');

$result = array ('res'=>false);

$mb_id = $member["mb_id"];
$idx = mysql_real_escape_string($_POST["idx"]);

$row = sql_fetch("SELECT * FROM `pini_console`.`AOSSettings` WHERE `build_idx`='$idx' and `mb_id`='$mb_id' ");
if($row){
	$result["res"] = true;
	$result["gameName"] 	= strlen($row["gameName"]) > 0 ? true : false;
	$result["packageName"] 	= strlen($row["packageName"]) > 5 ? true : false;
	$result["appVersion"] 	= strlen($row["appVersion"]) > 3 ? true : false;
	//$result["keystore"] 	= strlen($row["keystore"]) > 0 ? true : false;
	$result["password"] 	= strlen($row["password"]) > 8 ? true : false;
	$result["icon"]			= strlen($row["icon"]) > 0 ? true : false;

	$result["res"] = $result["gameName"] && $result["packageName"] && $result["appVersion"] && $result["password"] && $result["icon"];
}

echo json_encode($result);

?>