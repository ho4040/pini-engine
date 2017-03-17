<?php
$PINI_CONSOLE_MENU = 2;
include_once('./_common.php');

$result = array ('res'=>0);

$mb_id = $member["mb_id"];
$idx = mysql_real_escape_string($_GET["idx"]);

$row = sql_fetch("SELECT * FROM `pini_console`.`AOSSettings` WHERE `build_idx`='$idx' and `mb_id`='$mb_id' ");
if($row){
	$file = $row["apkpath"];
	$name = $row["gameName"];
	if (file_exists($file))
	{
		/*
	    if(false !== ($handler = fopen($file,"r")))
	    {
	        header('Content-Description: File Transfer');
	        header('Content-Type: application/octet-stream');
	        header('Content-Disposition: attachment; filename='.basename($name.".apk"));
	        header('Content-Transfer-Encoding: binary');
	        header('Expires: 0');
	        header('Cache-Control: must-revalidate, post-check=0, pre-check=0');
	        header('Pragma: public');
	        header('Content-Length: ' . filesize($file)); //Remove

	        //Send the content in chunks
	        while(false !== ($chunk = fread($handler,4096)))
	        {
	            echo $chunk;
	        }
	    	exit;
	    }
	    exit;*/
		header('Content-type: application/unknown');
		header('Content-Disposition: attachment; filename="'.$name.'.apk"');
		readfile($file);
	}
	echo "<h1>Content error</h1><p>The file does not exist! - 1</p>";
}else{
	echo "<h1>Content error</h1><p>The file does not exist! - 2</p>";
}
?>