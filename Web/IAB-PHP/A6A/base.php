<?php

include 'mysql.php';

function DebugMode($string) {
    if (false) {
        return $string;
    }
    else
        return "";
}



function logout() {
    //Start session
    session_start();

    //Unset the variables stored in session
    unset($_SESSION['SESS_USER_ID']);
    unset($_SESSION['SESS_FIRST_NAME']);
    unset($_SESSION['SESS_LAST_NAME']);
    unset($_SESSION['SESS_USER_LEVEL']);
    unset($_SESSION['SESS_USER_MAIL']);
}
function generateStrongPassword($length = 9, $add_dashes = false, $available_sets = 'luds')
{
    $sets = array();
    if(strpos($available_sets, 'l') !== false)
        $sets[] = 'abcdefghjkmnpqrstuvwxyz';
    if(strpos($available_sets, 'u') !== false)
        $sets[] = 'ABCDEFGHJKMNPQRSTUVWXYZ';
    if(strpos($available_sets, 'd') !== false)
        $sets[] = '23456789';
    if(strpos($available_sets, 's') !== false)
        $sets[] = '!@#$%&*?';

    $all = '';
    $password = '';
    foreach($sets as $set)
    {
        $password .= $set[array_rand(str_split($set))];
        $all .= $set;
    }

    $all = str_split($all);
    for($i = 0; $i < $length - count($sets); $i++)
        $password .= $all[array_rand($all)];

    $password = str_shuffle($password);

    if(!$add_dashes)
        return $password;

    $dash_len = floor(sqrt($length));
    $dash_str = '';
    while(strlen($password) > $dash_len)
    {
        $dash_str .= substr($password, 0, $dash_len) . '-';
        $password = substr($password, $dash_len);
    }
    $dash_str .= $password;
    return $dash_str;
}

//Function to sanitize values received from the form. Prevents SQL injection
function clean($str) {
$Link=DbConnection();

    $str = @trim($str);
    if (get_magic_quotes_gpc()) {
        $str = stripslashes($str);
    }
    $str=mysql_real_escape_string($str);
    DbDisconnect($Link);
    return $str;
}

function auth() {
    require_once('auth.php');
}

function register($Email, $Pass, $CPass, $Fname, $Lname, $Ulevel) {
    $link = DbConnection();
    //Start session
    session_start();

    //Array to store validation errors
    $errmsg_arr = array();

    //Validation error flag
    $errflag = false;


    //Sanitize the POST values
    $fname = clean($Fname);
    $lname = clean($Lname);
    $login = clean($Email);
    $password = clean($Pass);
    $cpassword = clean($CPass);
    $ulevel = clean($Ulevel);

    //Input Validations
    if ($ulevel == '') {
        $errmsg_arr[] = 'User level missing';
        $errflag = true;
    }
    if ($login == '') {
        $errmsg_arr[] = 'Email address missing';
        $errflag = true;
    }
    if ($password == '') {
        $errmsg_arr[] = 'Password missing';
        $errflag = true;
    }
    if ($cpassword == '') {
        $errmsg_arr[] = 'Confirm password missing';
        $errflag = true;
    }
    if (strcmp($password, $cpassword) != 0) {
        $errmsg_arr[] = 'Passwords do not match';
        $errflag = true;
    }

    //Check for duplicate login ID
    if ($login != '') {
        $qry = "SELECT * FROM logon WHERE useremail='$login'";
        $result = mysql_query($qry);
        if ($result) {
            if (mysql_num_rows($result) > 0) {
                $errmsg_arr[] = 'E-mail ID already in use';
                $errflag = true;
            }
            @mysql_free_result($result);
        } else {
            die("Query failed");
        }
    }
    DbDisconnect($link);
    //If there are input validations, redirect back to the registration form
    if ($errflag) {
        $_SESSION['ERRMSG_ARR'] = $errmsg_arr;
        session_write_close();
        header("location: register-form.php");
        exit();
    }
    $link = DbConnection();
    //Create INSERT query
    $qry = "INSERT INTO logon(firstname,lastname,useremail,userlevel,password) VALUES('$fname','$lname','$login','$ulevel','" . md5($password) . "')";

    $result = @mysql_query($qry);

    //Check whether the query was successful or not
    if ($result) {
        header("location: register-success.php");
        DbDisconnect($link);
        exit();
    } else {
        DbDisconnect($link);
        die("Query failed");
    }
}

function print_text($str, $Class, $Align='center', $lang="En") {
    if ($lang == "fa") {
        $Dir = 'rtl';
    } else {
        $Dir = 'ltr';
    }
    echo "<p class=\"$Class\" dir=\"$Dir\" align=\"$Align\" >$str</p>";
}

function upload($file_id='image', $folder="upload", $types="jpg", $max_file=1148576) {


//Create the upload directory with the right permissions if it doesn't exist
    if (!is_dir($folder)) {
        mkdir($folder, 0777);
        chmod($folder, 0777);
    }



    if (isset($_POST["upload"])) {

        //Get the file information
        $userfile_name = $_FILES['image']['name'];
        $userfile_tmp = $_FILES['image']['tmp_name'];
        $userfile_size = $_FILES['image']['size'];
        $filename = basename($_FILES['image']['name']);
        $file_ext = substr($filename, strrpos($filename, '.') + 1);

        //Only process if the file is a JPG and below the allowed limit
        if ((!empty($_FILES["image"])) && ($_FILES['image']['error'] == 0)) {
            if (($file_ext != $types) || ($userfile_size > $max_file)) {
                $error = "ONLY jpeg images under 1MB are accepted for upload";
                return array('err' => $error, 'addr' => '');
            }
        } else {
            $error = "Select a jpeg image for upload";
            return array('err' => $error, 'addr' => '');
        }
        //Everything is ok, so we can upload the image.
        if (strlen($error) == 0) {

            if (isset($_FILES['image']['name'])) {

                move_uploaded_file($userfile_tmp, $folder . '/' . $userfile_name);
            }
        }
    }
    return array('err' => $error, 'addr' => $folder . '/' . $userfile_name);
}



/**
Validate an email address.
Provide email address (raw input)
Returns true if the email address has the email 
address format and the domain exists.
*/
function validEmail($email)
{
   $isValid = true;
   $atIndex = strrpos($email, "@");
   if (is_bool($atIndex) && !$atIndex)
   {
      $isValid = false;
   }
   else
   {
      $domain = substr($email, $atIndex+1);
      $local = substr($email, 0, $atIndex);
      $localLen = strlen($local);
      $domainLen = strlen($domain);
      if ($localLen < 1 || $localLen > 64)
      {
         // local part length exceeded
         $isValid = false;
      }
      else if ($domainLen < 1 || $domainLen > 255)
      {
         // domain part length exceeded
         $isValid = false;
      }
      else if ($local[0] == '.' || $local[$localLen-1] == '.')
      {
         // local part starts or ends with '.'
         $isValid = false;
      }
      else if (preg_match('/\\.\\./', $local))
      {
         // local part has two consecutive dots
         $isValid = false;
      }
      else if (!preg_match('/^[A-Za-z0-9\\-\\.]+$/', $domain))
      {
         // character not valid in domain part
         $isValid = false;
      }
      else if (preg_match('/\\.\\./', $domain))
      {
         // domain part has two consecutive dots
         $isValid = false;
      }
      else if
(!preg_match('/^(\\\\.|[A-Za-z0-9!#%&`_=\\/$\'*+?^{}|~.-])+$/',
                 str_replace("\\\\","",$local)))
      {
         // character not valid in local part unless 
         // local part is quoted
         if (!preg_match('/^"(\\\\"|[^"])+"$/',
             str_replace("\\\\","",$local)))
         {
            $isValid = false;
         }
      }
      if ($isValid && !(checkdnsrr($domain,"MX") || 
 checkdnsrr($domain,"A")))
      {
         // domain not found in DNS
         $isValid = false;
      }
   }
   return $isValid;
}

?>
