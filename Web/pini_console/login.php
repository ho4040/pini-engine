<?php
$PINI_CONSOLE_MENU = 4;
include_once('./_common.php');

$g5['title'] = '개발자 콘솔';
include_once ('./console.head.php');

if($IS_LOGIN){
?>

<script>
document.location.href="../bbs/logout.php?url=../pini_console/index.php";
</script>

<?
}else{
?>

<script>
document.location.href="../bbs/login.php?url=../pini_console/index.php";
</script>

<?php
}

include_once ('./console.tail.php');
?>
