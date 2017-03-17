<?php

include ( 'ServeConfiguration.php');

function DbConnection($Db="-1") {

    $link = mysql_connect(DbServerAddress, DbServerUserName, DbServerPassword);
    if (!$link) {
        die('Failed to connect to server: ' . DebugMode(mysql_error()));
    }
    if ( $Db=="-1")
    {
        $db = mysql_select_db(DbDbName);
    }
    else 
    {
        $db = mysql_select_db($Db);
    }
        mysql_query("SET NAMES 'utf8'");
    if (!$db) {
        die("Unable to select database");
    }
    return $link;
}

function DbDisconnect($link) {
    mysql_close($link);
}

function FetchSqltoArray($qr,$Db="-1") {
    if ( $Db == -1)
    {
        $link = DbConnection();
    }
    else 
    {
        $link = DbConnection($Db);
    }
    mysql_query("SET NAMES 'utf8'");
    $result = mysql_query($qr);
    if ($result != "") {
        if (mysql_num_rows($result) == 0) { // table is empty 
            return null;
        }
    }
    else
        return null;
    $var = array();
    
    
    
    while ($temp = mysql_fetch_object($result)) {
        array_push($var, get_object_vars($temp));
    }
    DbDisconnect($link);

    return $var;
}

function runqr($qr) {

    return insert($qr);
}

function insert($qr) {
    $link = DbConnection();

    $res = mysql_query($qr);

    DbDisconnect($link);
    return $res;
}

function delete($qr) {
    return insert($qr);
}

