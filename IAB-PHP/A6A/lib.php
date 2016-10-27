<?php

function debug($str) {

    if (Debug)
        echo $str . "<br>";
}

function exportAsExcel($query, $HederName) {
    header("Content-Type: application/vnd.ms-excel; charset=utf-8");
    header("Content-Disposition: attachment; filename=filename.xls");
    header("Pragma: no-cache");
    header("Expires: 0");
//$HederName=  Array("id","Name");
//$query = "SELECT id,name FROM  jos_users" ;
    $res = FetchSqltoArray($query);


    foreach ($HederName as $Name) {
        echo $Name . "\t";
    }
    echo "\n\r";
    foreach ($res as $row) {
        foreach ($row as $clom) {


            print_r($clom . "\t");
        }
        echo "\n\r";
    }
}

function exportPdf($URl) {
    include('MPDF56/mpdf.php');


    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $URl);
    curl_setopt($ch, CURLOPT_HEADER, 0);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
    $html = curl_exec($ch);
    curl_close($ch);

    $mpdf = new mPDF('utf-8');
    $mpdf->SetAutoFont();

    $mpdf->WriteHTML($html);
    $mpdf->Output();
}

function GeneralDateToPersianDate($str) {

    $g_days_in_month = array(31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31);
    $str = preg_split('/ /', $str, -1, PREG_SPLIT_OFFSET_CAPTURE);
    $date = $str[0][0];
    $time = $str[1][0];
    $date = preg_split('/-/', $date, -1, PREG_SPLIT_OFFSET_CAPTURE);
    $time = preg_split('/:/', $time, -1, PREG_SPLIT_OFFSET_CAPTURE);
//    echo "H: ".$time[0][0]."<br>";
//    echo "M: ".$time[1][0]."<br>";
//    echo "S: ".$time[2][0]."<br>";
//    echo  "Y: ".$date[0][0]."<br>";
//    echo "M: ".$date[1][0]."<br>";
//    echo "D: ".$date[2][0]."<br>";

    $time[0][0] = $time[0][0] + 8;
    $time[1][0] = $time[1][0] + 30;
    if ($time[1][0] >= 60) {


        $time[1][0]-=60;
        $time[0][0]+=1;
    }
    if ($time[0][0] >= 24) {
        $time[0][0]-=24;
        $date[2][0]+=1;
        if ($date[2][0] >= $g_days_in_month[intval($date[1][0])]) {
            $date[2][0]-= $g_days_in_month[intval($date[1][0])];
            $date[1][0]+=1;
            if ($date[1][0] >= 12) {
                $date[1][0] = 1;
                $date[0][0]+=1;
            }
        }
    }




    $date = gregorian_to_jalali($date[0][0], $date[1][0], $date[2][0]);



    return $date[0] . "-" . $date[1] . "-" . $date[2] . " " . $time[0][0] . ":" . $time[1][0] . ":" . $time[2][0];
}

function convert($num) {
    $n = floatval(substr($num, 0, 2));
    $m = floatval(substr($num, 2));
    return floatval($n + $m / 60.0);
}

function SpeedConvert($Num) {
    return $Num;
}

function distance($lat1, $lon1, $lat2, $lon2, $unit) {

    $theta = $lon1 - $lon2;
    $dist = sin(deg2rad($lat1)) * sin(deg2rad($lat2)) + cos(deg2rad($lat1)) * cos(deg2rad($lat2)) * cos(deg2rad($theta));
    $dist = acos($dist);
    $dist = rad2deg($dist);
    $miles = $dist * 60 * 1.1515;
    $unit = strtoupper($unit);

    if ($unit == "K") {
        return ($miles * 1.609344);
    } else if ($unit == "N") {
        return ($miles * 0.8684);
    } else {
        return $miles;
    }
}

function CleanHackerTXT($text, $encode_ent = false) {
    $text = @trim($text);
    if ($encode_ent) {
        $text = htmlentities($text);
    }
    if (version_compare(phpversion(), '4.3.0') >= 0) {
        if (get_magic_quotes_gpc()) {
            $text = stripslashes($text);
        }
        if (@mysql_ping()) {
            $text = mysql_real_escape_string($text);
        } else {
            $text = addslashes($text);
        }
    } else {
        if (!get_magic_quotes_gpc()) {
            $text = addslashes($text);
        }
    }
    $text = strip_tags($text);
    $text = trim($text);
    return $text;
}

function del_dir($dir, $DeleteMe = TRUE) {
    if (!$dh = @opendir($dir))
        return;
    while (false !== ( $obj = readdir($dh) )) {
        if ($obj == '.' || $obj == '..')
            continue;
        if (!@unlink($dir . '/' . $obj))
            del_dir($dir . '/' . $obj, true);
    }

    closedir($dh);
    if ($DeleteMe) {
        @rmdir($dir);
    }
}

function att($is_admin=false) { // send true
    session_start();
    require_once 'ConfigPro.php';
    require_once 'function.php';
    $DomainName = strtolower($Domain);

    $refsite = $_SERVER['HTTP_REFERER'];
    $ref1 = trim($refsite);
//$ref1=strtolower($ref1);
    $ref1 = substr($ref1, 0, 38);
    $ref2 = preg_replace("/http:\/\//", "", $ref1);
    $ref3 = preg_replace("/www./", "", $ref2);
    $ref4 = explode("/", $ref3, 3);
    $ref5 = $ref4[0] . "/" . $ref4[1] . "/";
    $refsite = $ref5;

    $wmid = CleanHackerTXT($_SESSION['wmid']);
    $wmkey = CleanHackerTXT($_SESSION['wmkey']);

    $r3 = $_SERVER['SERVER_ADMIN'];
    $r3 = trim(strtolower($r3));

    if ((!$wmid) || (!$wmkey)) {
        session_destroy();
        header('Location: ' . "http://" . $refsite . "login.php?err=1");
        exit();
    } else {
        $tablename = "login";
        $link = mysql_connect($host, $user, $password);
        $query = "SELECT * FROM $tablename WHERE ((user='$wmid') AND (pass='$wmkey'))";
        $result = sql($query); //mysql_db_query ($dbname,$query,$link) OR die(mysql_error());
        $mn = mysql_num_rows($result);
        if ($mn <= "0") {
            session_destroy();
            header('Location: ' . "http://" . $refsite . "login.php?err=2");
            exit();
        }

        if ($is_admin) {
            if (is_admin() == false) {
                session_destroy();
                exit;
            }
        }
        $_SESSION['UID'] = $result['id'];
    }
}

function rand_char() {
    $c = array('u', '3', '4', '2', 'w', 'x', '5', '6', '7', 'K', 'L', 'c', 'd', 'M', 'N', '3', '4', 'P', 'Q', 'R', 'S', 'T', '8', '9', 'a', 'b', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'm', '2', '3', '4', '5', '6', '7', 'n', 'p', 'D', 'E', 'F', 'q', '4', '5', '6', 's', 'y', 'z', 'A', 'B', 'C', 'G', 'H', 'J', 'U', 'X', 'Y', 'Z', '8', 'V', 'W', '9');
    srand((double) microtime() * 10000000);
    $rc = array_rand($c);
    $char = $c[$rc];
    return $char;
}

function is_admin() {// this function check if username is equal to abarkam , return true .
    if ($_SESSION['wmid'] == 'abarkam')
        return true;
    return false;
}

function nl() {
    echo "<br/> \n";
}

//function insert($qr) {
//    $link = mysql_connect(DB_HOST, DB_USER, DB_PASSWORD);
//    if (!$link) {
//        die('Failed to connect to server: ' . mysql_error());
//    }
//    $db = mysql_select_db(DB_DATABASE);
//    if (!$db) {
//        die("Unable to select database");
//    }
//    return @mysql_query($qr);
//
//    //Check whether the query was successful or not
//}
//function sql($qr) {
//    //Connect to mysql server
//    $link = mysql_connect(DB_HOST, DB_USER, DB_PASSWORD);
//    if (!$link) {
//        die('Failed to connect to server: ' . mysql_error());
//    }
//
//    //Select database
//    $db = mysql_select_db(DB_DATABASE);
//    if (!$db) {
//        die("Unable to select database");
//    }
//    mysql_query("SET NAMES 'utf8'");
//    
//    $result = mysql_query($qr);
//
//    mysql_close($link);
//    return $result;
//}

function getExtension($str) {
    $i = strrpos($str, ".");
    if (!$i) {
        return "";
    }
    $l = strlen($str) - $i;
    $ext = substr($str, $i + 1, $l);
    return $ext;
}



function convert_2($str, $ky='') {
    if ($ky == ''
    )
        return $str;
    $ky = str_replace(chr(32), '', $ky);
    if (strlen($ky) < 8
    )
        exit('key error');
    $kl = strlen($ky) < 32 ? strlen($ky) : 32;
    $k = array();
    for ($i = 0; $i < $kl; $i++) {
        $k[$i] = ord($ky{$i}) & 0x1F;
    }
    $j = 0;
    for ($i = 0; $i < strlen($str); $i++) {
        $e = ord($str{$i});
        $str{$i} = $e & 0xE0 ? chr($e ^ $k[$j]) : chr($e);
        $j++;
        $j = $j == $kl ? 0 : $j;
    }
    return $str;
}

// make a tiket for new user not complate
function mktiket($id) {
    $tiket = (string) ($id) . ";" . (string) (date("m")) . ";" . (string) (date("y")) . ";" . (string) (date("d")) . ";";


    return convert(($tiket), KEY);
}

// find who creat tiket and or what service create this tiket . not complate

function rectiket($string) {
    $tiket = convert(($string), KEY);

    $a = preg_split('/;/', $tiket, -1, PREG_SPLIT_OFFSET_CAPTURE);

    if (date(m) > strval($a[1][0])
    )
        die("month expired");
    if (date(y) > strval($a[2][0])
    )
        die("year expired");
    if (date(d) > strval($a[3][0])
    )
        die("day expired");



    return strval($a[0][0]);
}

function cryp($str) {
    //    return ($str);
    return hash('crc32', strval($str));
    /*
      $string=null;
      $str=strval($str);
      //echo $str."<BR>";
      for( $i=1,$j=0;$i<=10 + (strlen($str)<=5 ? 1:0)  ; $i++ )
      {
      //echo $i."<BR>";
      //echo ."<br>";
      if ( ((4 - strlen($str))+2) <=$i && $i <= (strlen($str)+((4 - strlen($str))+2) ))
      {
      //  echo  $str[$j]."<BR>";
      $string=strval($string).strval($str[$j]);
      $j++;

      }
      else
      {
      $string=strval($string).strval(rand_char());
      }

      }
      return $string;
     */
    //return convert($str,KEY);
}

// a function to draw tabale not complate
function draw_tbl($result, $name, $cname="", $align="center") {// $result come from data base  , $name I dont remember is for what ,
    echo "<table border=\"1\"" . ( $align != "" ? " align=\"" . $align . "\"  >" : ">");

    echo "<tr>";
    foreach ($name as $n) {
        echo "<th>&nbsp&nbsp&nbsp&nbsp " . $n . " &nbsp&nbsp&nbsp&nbsp</th>";
    }
    echo "</tr>";
    if ($cname != "") {
        $name = $cname;
    }

    while ($row = mysql_fetch_array($result)) {
        foreach ($name as $n) {

            echo "<td>";
            echo "<p  align=\"center\">&nbsp&nbsp " . $row[$n] . "  &nbsp&nbsp</p> ";

            echo "</td>";
        }
        echo "</tr>";
    }
    echo "</table>";
}

function mkgr($id, $def, $temp=0) {// make main and defualt gerup directory
    $masterdir = MASTER_DIR;
    $patch_dis = PATCH_DIS;
    $dir = mkdir($masterdir . $patch_dis . cryp(strval($id)));
    $dir = mkdir($masterdir . PATCH_DIS . cryp(strval($id)) . PATCH_DIS . "temp");
    if ($def) {
        $qr = "INSERT INTO `cats` (`UID`, `name`,`Ctype`) VALUES ('" . strval($id) . "', 'بنرهاي محصولات','1') ,('" . strval($id) . "', 'تصاوير بزرگ محصولات','1') , ('" . strval($id) . "', 'تصوير كوچك محصولات','1')";

        $dir = insert($qr);
        if ($dir) {
            $qr = "select CID from cats where `UID`=" . $id . " and `name`='تصوير كوچك محصولات'";
            ////  echo $qr."<br>";
            $res = sql($qr);
            $res = mysql_fetch_array($res);
            $res = $res['CID'];
            //echo $res."<br>";
            $dir = mkdir($masterdir . $patch_dis . cryp(strval($id)) . $patch_dis . cryp(strval($res)));
            $qr = "select CID from cats where `UID`=" . $id . " and `name`='تصاوير بزرگ محصولات'";
            //echo $qr."<br>";
            $res = sql($qr);
            $res = mysql_fetch_array($res);
            $res = $res['CID'];
            //echo $res."<br>";
            $dir = mkdir($masterdir . $patch_dis . cryp(strval($id)) . $patch_dis . cryp(strval($res)));
            $qr = "select CID from cats where `UID`=" . $id . " and `name`='بنرهاي محصولات'";
            //echo $qr."<br>";
            $res = sql($qr);
            $res = mysql_fetch_array($res);
            $res = $res['CID'];
            //echo $res."<br>";
            $dir = mkdir($masterdir . $patch_dis . cryp(strval($id)) . $patch_dis . cryp(strval($res)));
        }
    }
    return $dir;
}

function mkgroup($UID, $name) {
    $query = "INSERT INTO cats values (NULL,'$UID','$name',NULL)";
    //echo $query."<BR>";
    $dir = insert($query);
    $query = "select CID from cats where `UID`='" . $UID . "' and `name`='" . $name . "'";
    //echo $query."<BR>";
    $cid = sql($query);
    $cid = mysql_fetch_array($cid);
    $cid = $cid['CID'];
    //echo $cid."<BR>";
    $dir = mkdir(MASTER_DIR . PATCH_DIS . cryp($UID) . PATCH_DIS . cryp(strval($cid)));
    return $dir;
}

function delgrp($id) {// remove a directory
    del_dir(MASTER_DIR . PATCH_DIS . cryp($id));

    $qr = "DELETE FROM `cats` WHERE `UID` = " . $id;
    sql($qr);

    return true;
}

function deldir($patch) {// remove a directory
    if (is_dir($parch)) {
        echo $patch . "<br>";

        $dirs = scandir($patch);
        print_r($dirs);
        if (count($dirs) > 2) {
            foreach ($dirs as $dir) {
                if ($dir != "." && $dir != "..") {
                    // echo ($masterdir.$patch_dis.cryp(strval($id)).$patch_dis.$dir.$patch_dis)."<br>";
                    $fils = scandir($patch . $patch_dis . $dir);
                    foreach ($fils as $file) {
                        if ($file != "." && $file != "..") {
                            //  echo ($masterdir.$patch_dis.cryp(strval($id)).$patch_dis.$dir.$patch_dis.$file)."<br>";
                            unlink($patch . $patch_dis . $dir . $patch_dis . $file);
                        }
                    }
                    rmdir($patch . $patch_dis . $dir);
                }
            }
        }

        rmdir($patch);
    }
    return true;
}

function delgroup($cid, $id) {

    $masterdir = MASTER_DIR;
    $patch_dis = PATCH_DIS;
    $base_dir = $masterdir . $patch_dis . cryp(strval($id)) . PATCH_DIS . cryp($cid);
    //echo $base_dir."<BR>";
    if (is_dir($base_dir)) {
        $dirs = scandir($base_dir);

        if (count($dirs) > 2) {

            foreach ($dirs as $dir) {
                if ($dir != "." && $dir != "..") {

                    $fils = scandir($base_dir . PATCH_DIS . cryp($cid) . $patch_dis . $dir);
                    foreach ($fils as $file) {
                        if ($file != "." && $file != "..") {

                            unlink($base_dir . $patch_dis . $dir . $patch_dis . $file);
                        }
                    }
                    rmdir($base_dir . $patch_dis . $dir);
                }
            }
        }

        rmdir($masterdir . $patch_dis . cryp(strval($id)) . PATCH_DIS . cryp($cid));
        $qr = "DELETE FROM `cats` WHERE `CID` = " . $cid;
        if (sql($qr)) {
            //echo " rmdir2 true <br>";
            return true;
        }
        else
            return false;
    }
    return false;
}

function get_ftype($t) {
    $type = strtolower($t);


    switch ($type) {
        case "jpg":
        case "jpeg":
            return 0;
            break;
        case "gif":
            return 1;
            break;
        case "png":
            return 2;
            break;
        case "doc":
            return 3;
            break;
        case "zip":
            return 4;
            break;
        default :
            return -1;
            break;
    }
}

function get_ftype_name($type) {



    switch ($type) {
        case "0":
            return "jpg";
            break;
        case "1":
            return "gif";

            break;
        case "2":
            return "png";

            break;
        case "3":
            return "doc";

            break;
        default :
            return "";
            break;
    }
}

/*
  function upload($file_id, $folder="", $types="") {
  if (!$_FILES[$file_id]['name'])
  return array('', 'No file specified');

  $file_title = $_FILES[$file_id]['name'];
  //Get file extension
  $ext_arr = preg_split('/\./', basename($file_title));


  $ext = strtolower($ext_arr[count($ext_arr) - 1]); //Get the last extension
  //Not really uniqe - but for all practical reasons, it is
  $uniqer = substr(md5(uniqid(rand(), 1)), 0, 5);
  //$file_name = $uniqer . '_' . $file_title;//Get Unique Name
  $file_name = $file_title;
  $all_types = explode(",", strtolower($types));
  if ($types) {
  if (in_array($ext, $all_types)

  );
  else {

  $str = "<h2 dir=\"rtl\" style=\"color:red;\"> خطا  !! </h2>
  <h2  dir=\"rtl\">	فايل غير مجاز است ، فقط پسوند هاي زير مجاز است . <br>	gif - jpg - png - bmp - doc - zip - rar
  </h2><a href='javascript:history.go(-1)' class=\"titr\" dir=\"rtl\" align=\"center\"> برگشت (Back)</a> \n";

  $result = $str; //"'".$_FILES[$file_id]['name']."' is not a valid file."; //Show error if any.
  return array('', $result);
  }
  }

  //Where the file must be uploaded to
  if ($folder)
  $folder .= '/'; //Add a '/' at the end of the folder
  $uploadfile = $folder . $file_name;

  $result = '';
  //Move the file from the stored location to the new location
  if (!move_uploaded_file($_FILES[$file_id]['tmp_name'], $uploadfile)) {
  $result = "Cannot upload the file '" . $_FILES[$file_id]['name'] . "'"; //Show error if any.
  if (!file_exists($folder)) {
  $result .= " : Folder don't exist.";
  } elseif (!is_writable($folder)) {
  $result .= " : Folder not writable.";
  } elseif (!is_writable($uploadfile)) {
  $result .= " : File not writable.";
  }
  $file_name = '';
  } else {
  if (!$_FILES[$file_id]['size']) { //Check if the file is made
  @unlink($uploadfile); //Delete the Empty file
  $file_name = '';
  $result = "Empty file found - please use a valid file."; //Show the error message
  } else {
  chmod($uploadfile, 0777); //Make it universally writable.
  }
  }

  return array($file_name, $result, get_ftype($ext), $_FILES[$file_id]['size']);
  }

  function upload_test($file_id,$folder="",$types="")
  {


  }



  /*



  function att()
  {
  session_start();
  require_once 'ConfigPro.php';
  require_once 'function.php';
  $DomainName=strtolower($Domain);

  $refsite=$_SERVER['HTTP_REFERER'];
  $ref1 =trim($refsite);
  //$ref1=strtolower($ref1);
  $ref1=substr($ref1,0,38);
  $ref2 =preg_replace("/http:\/\//","",$ref1);
  $ref3 =preg_replace("/www./","",$ref2);
  $ref4 =explode("/",$ref3,3);
  $ref5 =$ref4[0]."/".$ref4[1]."/";
  $refsite=$ref5;

  $wmid = CleanHackerTXT($_SESSION['wmid']);
  $wmkey = CleanHackerTXT($_SESSION['wmkey']);

  $r3=$_SERVER['SERVER_ADMIN'];	$r3=trim(strtolower($r3));

  if ((!$wmid) || (!$wmkey) ){
  session_destroy(); header('Location: '."http://".$refsite."login.php?err=1");exit();
  }else {
  $tablename="login";
  $link = mysql_connect ($host,$user,$password);
  $query = "SELECT * FROM $tablename WHERE ((user='$wmid') AND (pass='$wmkey'))";
  $result = sql($query);//mysql_db_query ($dbname,$query,$link) OR die(mysql_error());
  $mn = mysql_num_rows($result);
  if ($mn<="0"){
  session_destroy(); header('Location: '."http://".$refsite."login.php?err=2");exit();
  }

  }
  }
 */

function remot_file_uploder($remote_file, $target, $valid=null) {
    if (isset($remote_file)) {

        $filename = basename($remote_file);
        $ftype = getExtension($filename);
        if ($valid != NULL) {
            if (!in_array(strtolower($ftype), $valid)) {
                return array("Upload ERROR: File type not match", false, $filename);
            }
        }
        $target = $target . PATCH_DIS . $filename;
        if (!@copy($remote_file, $target)) {
            $errors = error_get_last();
            $msg = "Upload ERROR: " . $errors['type'] . "<br />\n" . $errors['message'];
            return array($msg, false);
        } else {
            $msg = "File copied from remote!";
            return array($msg, true, $filename);
        }
    }
}

function img_uploader($file, $CID, $target_path, $mode, $UpdateMode=false, $tozihat="it`s a group upload file", $code=NULL, $NW=-1, $NH=-1) {
    $image = $file;
    $uploadedfile = $target_path . PATCH_DIS . $file;
    if ($code == NULL) {
        $codeKala = basename($target_path);
    } else {
        $codeKala = $code;
    }
    debug(" codeKala parsing in Img_Uploader function " . $codeKala);
    debug($image . " <= image " . $uploadedfile . " <= uploadedfile " . $CID . " <= CID<br>");
    $UID = $_SESSION['UID'];
    $filename = stripslashes($file);
    $extension = getExtension($filename);
    $extension = strtolower($extension);
    $ftype = get_ftype($extension);
    debug("file extention is : " . $extension);
    if (($extension != "jpg") && ($extension != "jpeg") && ($extension != "png") && ($extension != "gif")) {
        debug("this is not a valid file and should be deleted");
        unlink($uploadedfile);
        print_text("دسوند این فایل جزو پسوند های مجاز نمی باشد", "err");
        return;
    } else {
        debug("start prossesing image file");
        $size = filesize($uploadedfile);

        debug($uploadedfile . " size is : " . $size);

        if ($size > MAX_SIZE * 1024) {
            unlink($uploadedfile);
            print_text("سایز این عکس از حد مجاز بیشتر است", "err");
            return;
        }
        if ($extension == "jpg" || $extension == "jpeg") {
            $uploadedfile = $uploadedfile;
            $src = imagecreatefromjpeg($uploadedfile);
        } else if ($extension == "png") {
            $uploadedfile = $uploadedfile;
            $src = imagecreatefrompng($uploadedfile);
        } else {

            $src = imagecreatefromgif($uploadedfile);
            echo $src;
            echo " test <br><br><br><br><br><br><br>";
        }

        debug("image size and format is valid and started for prosesiing " . $src);

        list($width, $height) = getimagesize($uploadedfile);
        debug("w : " . $width . " and h : " . $height);

        if ($mode == SII) {

            $newwidth = 200;
            $newheight = 160; //($height/$width)*$newwidth;
        } else if ($mode == LII) {
            debug("nw that send is : " . $NW);
            $newwidth = ($NW == -1 ? 450 : $NW);
            $newheight = ($NH == -1 ? ($height / $width) * $newwidth : $NH);
        } else if ($mode == BII) {

            $newwidth = ($NW == -1 ? $width : $NW);
            $newheight = ($NH == -1 ? $height : $NH);
        }
        $tmp = imagecreatetruecolor($newwidth, $newheight);

        imagecopyresampled($tmp, $src, 0, 0, 0, 0, $newwidth, $newheight, $width, $height);
        debug(" New w : " . $newwidth . " and New h : " . $newheight);

        // imagecopyresampled($tmp1,$src,0,0,0,0,$newwidth1,$newheight1,$width,$height);

        $base_address = MASTER_DIR . PATCH_DIS . cryp($UID) . PATCH_DIS . cryp($CID) . PATCH_DIS;
        debug("this file will moved to " . $base_address);

        $filename = $base_address . $image;
        debug("and final file address will be : " . $filename);

        //echo $filename."<br>";
        //$filename1 = "images/small". $_FILES['file']['name'];

        require_once ('farsi_date.php');
        $date = ShamsiDate('a');

        if ($extension == 'gif') {
            echo "gift extention is detected";

            if ($mode == BII) {
                move_uploaded_file($uploadedfile, $filename);
            } else {
                $RRes = imagegif($tmp, $filename);
            }
        } else if ($extension == 'jpg' || $extension == 'jpeg') {
            $RRes = imagejpeg($tmp, $filename, 100);
        } else if ($extension == 'png') {
            $RRes = imagepng($tmp, $filename, 100);
        }



        if ($RRes) {
            ?>

            <h2 dir="rtl" ><p class="text">  فایل با موفقیت به سرور انتقال پیدا کرد و از ادرس زیر قابل دسترس می باشد.<br></p></h2>



            <center><br>
            <?
            echo"<h1 dir=\"rtl\" class=\"t3\">حجم فايل : <span style=\"color:red;\">" . $size . "</span> &nbsp; &nbsp; &nbsp;   تاريخ ثبت : <span style=\"color:red;\">$date</span><br><br><textarea name=\"fffile\" id=\"fffile\" cols=\"90\" rows=\"2\" dir=\"ltr\" onClick=\"javascript:this.select();\">" . Domain . $filename . "</textarea>
				<br><input type=\"button\" class=\"text\" dir=\"rtl\" onClick=\"copytoclipboard('fffile');\" value=\" كپي \"></h1>";

            if (($extension == "gif") || ($extension == "jpg") || ($extension == "jpeg") || ($extension == "png") || ($extension == "bmp")) {
                echo"<br><a href=\"$fileaddress\" target=\"_blank\" dir=rtl><img src=\"$filename\" border=\"0\" alt=\"" . $_FILES['file1']['name'] . "\"></a>";
            } elseif ($extension == "swf") {
                ?><br><object classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" dir="rtl" codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=7,0,0,0">
                        <param name="flash_component" value="ImageViewer.swc">
                        <param name="movie" value="<? echo"$fileaddress"; ?>">
                        <param name="quality" value="high">
                        <param name="FlashVars" value="flashlet={imageLinkTarget:'_blank',captionFont:'Verdana',titleFont:'Verdana',showControls:true,frameShow:false,slideDelay:5,captionSize:10,captionColor:#333333,titleSize:10,transitionsType:'Random',titleColor:#333333,slideAutoPlay:false,imageURLs:['img1.jpg','img2.jpg','img3.jpg'],slideLoop:false,frameThickness:2,imageLinks:['http://macromedia.com/','http://macromedia.com/','http://macromedia.com/'],frameColor:#333333,bgColor:#FFFFFF,imageCaptions:[]}">
                        <embed src="<? echo"$filename"; ?>" quality="high" flashvars="flashlet={imageLinkTarget:'_blank',captionFont:'Verdana',titleFont:'Verdana',showControls:true,frameShow:false,slideDelay:5,captionSize:10,captionColor:#333333,titleSize:10,transitionsType:'Random',titleColor:#333333,slideAutoPlay:false,imageURLs:['img1.jpg','img2.jpg','img3.jpg'],slideLoop:false,frameThickness:2,imageLinks:['http://macromedia.com/','http://macromedia.com/','http://macromedia.com/'],frameColor:#333333,bgColor:#FFFFFF,imageCaptions:[]}" pluginspage="http://www.macromedia.com/shockwave/download/index.cgi?P1_Prod_Version=ShockwaveFlash" type="application/x-shockwave-flash"></embed>
                    </object><?
            } elseif (($extension == "rar") || ($extension == "zip")) {
                echo"<br><a href=\"$fileaddress\" dir=\"rtl\" style=\"text-decoration:none; font-size:8pt; color:#000; font-family:Tahoma, sans-serif;\" title=\" دانلود \"><img src=\"http://www.$DomainName/rar-zip-small.gif\" alt=\"دانلود $fname\" width=\"20\" height=\"15\" border=\"0\" align=\"absmiddle\"> دانلود فايل ( $filesize )</a>";
            }
            ?><a href='javascript:history.go(-1)' class="titr" dir="rtl" align="center"><h4> برگشت (Back)</h4></a>
            </center>

            <?php
            $ftype = get_ftype($extension);
            $fsize = filesize($filename);

            ##### ذخيره داده ها در پايگاه داده
            if ($UpdateMode == false)
                $qr = "INSERT INTO `files` (`fid`, `CID`, `fname`, `ftype`, `fsize`, `UID`, `date`, `tovzihat`, `codeKala`) VALUES (NULL, '" . $CID . "', '" . $image . "', '" . $ftype . "', '" . $size . "', '" . $UID . "', '" . $date . "', '" . $tozihat . "', '" . $codeKala . "')";
            else
                $qr = "UPDATE `files` SET  `fname` =  '" . $image . "',`fsize` =  '" . $size . "' WHERE  `fid` ='" . $UpdateMode . "'";


            debug("query that used to insert data is : " . $qr);

            if (insert($qr)) {

                $qr = "select usedsize from login where `id`=" . $_SESSION['UID'];
                $res = sql($qr);
                $res = mysql_fetch_array($res);
                $usedsize = $res['usedsize'];
                $usedsize+=$fsize;
                $qr = "UPDATE  `login` SET  `usedsize` =  '" . $usedsize . "' WHERE  `login`.`id` =" . $_SESSION['UID'];
                if (sql($qr)) {
                    // echo "all information stored in Database too<br>";
                } else {
                    print_text("Error in insertion information in database <br>", "err");
                }
            } else {
                print_text("Error in insertion information in database  2<br>", "err");
            }
        }
        imagedestroy($src);
        imagedestroy($tmp);
    }
}

function is_codeKala($str) {
    if ($str[0] == "#")
        return true;
    return false;
}

function scan_dir($target_path, $dep, $Kala=false) {

    if ($Kala) {
        $UID = $_SESSION['UID'];
        $qr = "select * from cats where UID=" . $UID;
        debug("query for category selection : " . $qr);
        $BCID = 0;
        $SCID = 0;
        $LCID = 0;
        $res = sql($qr);
        while ($row = mysql_fetch_array($res)) {

            if ($row['name'] == "تصاوير بزرگ محصولات") {
                $LCID = $row['CID'];
            } else if ($row['name'] == "تصوير كوچك محصولات") {
                $SCID = $row['CID'];
            } else if ($row['name'] == "بنرهاي محصولات") {
                $BCID = $row['CID'];
            }
        }
        debug("LCID is " . $LCID);
        debug("SCID is " . $SCID);
        debug("BCID is " . $BCID);
        $codeKala = basename(substr($target_path, 1));
        debug(" in kala mode , target that detected is " . $target_path);
        debug(" codeKala is : " . $codeKala);

        $dir = opendir($target_path);
        while ($file = readdir($dir)) {
            if ($file == SII || $file == LII || $file == BII) {
                debug("start directry parsing : file detected is :" . $file);

                $handele = opendir($target_path . PATCH_DIS . $file);
                while ($file2 = readdir($handele)) {


                    if ($file2 != '.' && $file2 != '..') {
                        if (!is_dir($target_path . PATCH_DIS . $file . PATCH_DIS . $file2)) {

                            debug(" scaned target and find this File / Dir  this file should not be . or .. or any other thing: " . $file2);

                            if (strtolower(getExtension($file2)) == 'jpg' || strtolower(getExtension($file2)) == 'jpeg' || strtolower(getExtension($file2)) == 'gif' || strtolower(getExtension($file2)) == 'png') {// file2 is a valid image file
                                $UID = $_SESSION['UID'];
                                $qr = "select * from cats where UID=" . $UID;
                                debug("query for category selection : " . $qr);
                                $BCID = 0;
                                $SCID = 0;
                                $LCID = 0;
                                $res = sql($qr);
                                while ($row = mysql_fetch_array($res)) {

                                    if ($row['name'] == "تصاوير بزرگ محصولات") {
                                        $LCID = $row['CID'];
                                    } else if ($row['name'] == "تصوير كوچك محصولات") {
                                        $SCID = $row['CID'];
                                    } else if ($row['name'] == "بنرهاي محصولات") {
                                        $BCID = $row['CID'];
                                    }
                                }
                                debug("LCID is " . $LCID);
                                debug("SCID is " . $SCID);
                                debug("BCID is " . $BCID);
                                $codeKala = basename(substr($target_path, 1));
                                debug(" in kala mode , target that detected is " . $target_path);
                                debug(" codeKala is : " . $codeKala);


                                debug(" this file is an valid image that set in config file and can be moved to correct directory");
                                $is_smale_pic_and_should_go_away = false;
                                if ($file == BII)
                                    $CCID = $BCID;
                                elseif ($file == LII)
                                    $CCID = $LCID;
                                elseif ($file == SII) {
                                    $CCID = $SCID;
                                    $is_smale_pic_and_should_go_away = true;
                                }
                                debug(" CID is : " . $CCID);
                                debug(" File is : " . $file);
                                img_uploader($file2, ($CCID), $target_path . PATCH_DIS . $file, $file, false, "it`s a group upload file", $codeKala);
                                if (is_file($target_path . PATCH_DIS . $file . PATCH_DIS . $file2))
                                    unlink($target_path . PATCH_DIS . $file . PATCH_DIS . $file2);
                                if ($is_smale_pic_and_should_go_away) {

                                    del_dir($target_path . PATCH_DIS . $file);
                                    break;
                                }
                            } else {// file 2 is not a valid image file and should be delated
                                debug("this file is not an image and sould be deleted");
                                unlink($target_path . PATCH_DIS . $file . PATCH_DIS . $file2);
                                debug("file that should delete: " . $target_path . PATCH_DIS . $file . PATCH_DIS . $file2);
                            }
                        } else {// file 2 is a directory
                            debug("this file is not a file and should be deleted all of directory ");

                            del_dir($target_path . PATCH_DIS . $file . PATCH_DIS . $file2);
                        }
                    }
                }
                closedir($handele);
            } else {
                if ($file != '.' && $file != '..') {
                    if (is_dir($target_path . PATCH_DIS . $file)) {
                        del_dir($target_path . PATCH_DIS . $file);
                    } else {
                        unlink($target_path . PATCH_DIS . $file);
                    }
                }
            }
        }

        del_dir($target_path);
        return;
    } else {

        $handel1 = opendir($target_path);
        while ($file = readdir($handel1)) {
            if ($file != "." && $file != ".." && $file != "__MACOSX" && $file != ".DS_Store") {
                if (is_dir($target_path . PATCH_DIS . $file)) {
                    // echo  $dep.$file."/<br>";
                    if (is_codeKala($file)) {/// change !!!!
                        scan_dir($target_path . PATCH_DIS . $file, $dep . "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;", true);
                    } else {
                        scan_dir($target_path . PATCH_DIS . $file, $dep . "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;");
                    }
                    del_dir($target_path . PATCH_DIS . $file);
                } else {
                    unlink($target_path . PATCH_DIS . $file);
                }
            } else {
                if ($file != "." && $file != "..") {

                    if (is_dir($target_path . PATCH_DIS . $file)) {
                        //   echo "I find a dir ".$target_path.PATCH_DIS.$file."<br>";

                        del_dir($target_path . PATCH_DIS . $file);
                    } else {
                        //chmod($target_path.PATCH_DIS.$filename, "0777");

                        unlink($target_path . PATCH_DIS . $file);
                    }
                }
            }
        }
    }
}

function txtonimg($src, $str, $color, $x, $y) {

    $font = 'ANGSAZ.TTF';
    $string = $str; // String
    $filename = basename($src);
    $ext = getExtension($filename);
    if (strtolower($ext) == "gif")
        $im = imagecreatefromgif($src); // Path Images
    elseif (strtolower($ext) == "jpg" || strtolower($ext) == "jpeg")
        $im = imagecreatefromjpeg($src); // Path Images
    elseif (strtolower($ext) == "png")
        $im = imagecreatefrompng($src); // Path Images

    $color = ImageColorAllocate($im, 255, 255, 255); // Text Color

    $pxX = (Imagesx($im) - 4 * strlen($string)) / 2; // X
    $pxY = Imagesy($im) - 10; // Y
    ImagettfText($im, 20, 0, $pxX, $pxY, $color, $font, $string);
    if (strtolower($ext) == "gif")
        imagegif($src);
    elseif (strtolower($ext) == "jpg" || strtolower($ext) == "jpeg")
        imagejpeg($src);
    elseif (strtolower($ext) == "png")
        imagepng($src);


    ImageDestroy($im);
}

function SetDomain() {
    return "http://" . $_SERVER['HTTP_HOST'] . "/" . INSTALL_DIR . "";
}

class ZipFolder {

    protected $zip;
    protected $root;
    protected $ignored_names;

    function __construct($file, $folder, $ignored=null) {
        $this->zip = new ZipArchive();
        $this->ignored_names = is_array($ignored) ? $ignored : $ignored ? array($ignored) : array();
        if ($this->zip->open($file, ZIPARCHIVE::CREATE) !== TRUE) {
            throw new Exception("cannot open <$file>\n");
        }
        $folder = substr($folder, -1) == '/' ? substr($folder, 0, strlen($folder) - 1) : $folder;
        if (strstr($folder, '/')) {
            $this->root = substr($folder, 0, strrpos($folder, '/') + 1);
            $folder = substr($folder, strrpos($folder, '/') + 1);
        }
        $this->zip($folder);
        $this->zip->close();
        return true;
    }

    function zip($folder, $parent=null) {
        $full_path = $this->root . $parent . $folder;
        $zip_path = $parent . $folder;
        $this->zip->addEmptyDir($zip_path);
        $dir = new DirectoryIterator($full_path);
        foreach ($dir as $file) {
            if (!$file->isDot()) {
                $filename = $file->getFilename();
                if (!in_array($filename, $this->ignored_names)) {
                    if ($file->isDir()) {
                        $this->zip($filename, $zip_path . '/');
                    } else {
                        $this->zip->addFile($full_path . '/' . $filename, $zip_path . '/' . $filename);
                    }
                }
            }
        }
        return true;
    }

}
?>
