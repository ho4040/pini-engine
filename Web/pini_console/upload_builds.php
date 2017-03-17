<?php
$PINI_CONSOLE_MENU = 2;
include_once('./_common.php');

if($member["mb_id"] == ""){
	print("<font color='red'>로그인이 필요합니다.</font><br>");
	exit();
}

$mb_id = $member["mb_id"];

?>
<?php
// 4.1.0 이전의 PHP에서는, $_FILES 대신에 $HTTP_POST_FILES를
// 사용해야 합니다.

$result = array ('res'=>0,'msg'=>"");
$msg = "";
$msg.= '<pre>';

$projName = mysql_real_escape_string($_POST["projName"]);
if(strlen($projName) > 3){
	$uploaddir  = './upload/build/';
	$uploadfile = $uploaddir . md5(basename($_FILES['userfile']['name']).time());

	$count = 0;
	$tmp = $uploadfile;
	while(1){
		$msg .= $tmp;
		if(file_exists( $tmp.".zip" )){
			$tmp = $uploadfile.$count;
			$count++;
		}else{
			break;
		}
	}
	$uploadfile = $tmp.".zip";

	if (move_uploaded_file($_FILES['userfile']['tmp_name'], $uploadfile)) {
		$msg.= "파일이 유효하고, 성공적으로 업로드 되었습니다.\n";
	} else {
		$msg.= "업로드에 실패하였습니다!\n";
	}

	$za = new ZipArchive(); 
	$isBuildZip = false;
	$ret = $za->open($uploadfile);
	if($ret===true){ 
		$msg.= 'ZIP 파일을 엽니다.<br>';
		for( $i = 0; $i < $za->numFiles; $i++ ){ 
			$stat = $za->statIndex( $i ); 
			$filename = basename( $stat['name'] );
			if($filename == "ProjectInfo.lua"){
				$isBuildZip = true;
				break;
			}
		}
	}else{
		$msg.= "<font color='red'>zip 파일이 아닙니다. 다시 업로드 해주세요.</font><br>";
	}
	if($isBuildZip){
		$msg.= "<font color='green'>업로드가 정상적으로 처리되었습니다.</font><br>";
		$size = filesize($uploadfile);
		$sql = "INSERT INTO `pini_console`.`builds`
				(`idx`, `mb_id`, `filename`, `projname`, `capacity` ,`datetime`) VALUES
				(NULL, '$mb_id', '$uploadfile', '$projName', '$size', CURRENT_TIMESTAMP);";
		sql_query($sql);

		$fetch = sql_fetch("SELECT idx FROM `pini_console`.`builds` WHERE filename='$uploadfile'");

		$result["res"] = 1;
		$result["idx"] = $fetch["idx"];

	}else{
		$msg.= "<font color='red'>Build폴더가 아닙니다. 클린테스트 진행 후 build폴더를 다시 압축하여 업로드 해주시기 바랍니다.</font><br>";
		unlink($uploadfile);
	}
}else{
	$msg.= "<font color='red'>프로젝트 이름을 제대로 설정하십시오.</font><br>";
}
$msg.= "</pre>";

$result["msg"] = $msg;
echo json_encode($result);
?>