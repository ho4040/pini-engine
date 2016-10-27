<?php
include_once('./_common.php');

if($member["mb_id"] == ""){
	print("<font color='red'>로그인이 필요합니다.</font><br>");
	exit();
}

$idx = mysql_real_escape_string($_POST["idx"]);
$mb_id = $member["mb_id"];

$row = sql_fetch("SELECT * FROM `pini_console`.`builds` WHERE idx='$idx' and mb_id='$mb_id' ");
unlink($row["filename"]);

sql_fetch("DELETE FROM `pini_console`.`builds` WHERE `builds`.`idx`=$idx and mb_id='$mb_id' ");
?>