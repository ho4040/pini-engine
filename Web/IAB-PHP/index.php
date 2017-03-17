<?php
define('PUBLIC_KEY', '내 개발자 공개키');
define('PACKAGE_NAME', '내 게임 패키지명(안드로이드 익스포팅 시 적었던 패키지명)');

$orderID = "";
$purchaseToken = "";
$developerPayload = "";
$packageName = "";
$purchaseState = "";
$purchaseTime = "";
$productId = "";

require_once("A6A/base.php");
require_once("A6A/lib.php");
require_once("verify.php");

$jsonData = $_POST['data'];
$json = json_decode($jsonData);

$responseData = $json->{'purchaseData'};
$signature = $json->{'dataSignature'};

$result = array("result"=>0);
if (verifySignatureTransaction($responseData, $signature, PUBLIC_KEY)) {
    $responseData = str_replace("{", "", $responseData);
    $responseData = str_replace("}", "", $responseData);
    $parts = explode(',', $responseData);

    for ($i = 0; $i < count($parts); $i++) {
        $data = explode(':', $parts[$i]);

        $temp = str_replace('"', "", $data[0]);
        $temp = trim($temp);
        if ($temp == "orderId") {
            $orderID = str_replace('"', "", $data[1]);
        }else if ($temp == "purchaseToken") {
            $purchaseToken = str_replace('"', "", $data[1]);
        }else if ($temp == "developerPayload") {
            $developerPayload = str_replace('"', "", $data[1]);
        }else if ($temp == "packageName") {
            $packageName = str_replace('"', "", $data[1]);
        }else if ($temp == "purchaseState") {
            $purchaseState = str_replace('"', "", $data[1]);
        }else if ($temp == "purchaseTime") {
            $purchaseTime = str_replace('"', "", $data[1]);
        }else if ($temp == "productId") {
            $productId = str_replace('"', "", $data[1]);
        }
    }

    if (empty($orderID) || $orderID == "") {
        die(json_encode($result));
    } else if (empty($purchaseToken) || $purchaseToken == "") {
        die(json_encode($result));
    } else if (empty($developerPayload) || $developerPayload == "") {
        die(json_encode($result));
    } else if (empty($packageName) || $packageName == "") {
        die(json_encode($result));
    } else if($purchaseState == "") {
        die(json_encode($result));
    } else if (empty($purchaseTime) || $purchaseTime == "") {
        die(json_encode($result));
    } else if (empty($productId) || $productId == "") {
        die(json_encode($result));
    }

    if (trim($packageName) != PACKAGE_NAME) {
        die(json_encode($result));
    }


    $productId = trim($productId);

    //////
    // orderId, productId등 변수를 디비에 저장해 중복 결제를 막을 수 있습니다.
    //////

    $result["result"] = 1;
    $result["productId"] = $productId;
    echo json_encode($result);
} else {
    echo json_encode($result);
}
?>