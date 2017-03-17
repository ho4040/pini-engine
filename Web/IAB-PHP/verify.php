<?php
define(BILLING_RESPONSE_RESULT_OK, 0);
define(BILLING_RESPONSE_RESULT_USER_CANCELED, 1);
define(BILLING_RESPONSE_RESULT_BILLING_UNAVAILABLE, 3);
define(BILLING_RESPONSE_RESULT_ITEM_UNAVAILABLE, 4);
define(BILLING_RESPONSE_RESULT_DEVELOPER_ERROR, 5);
define(BILLING_RESPONSE_RESULT_ERROR, 6);
define(BILLING_RESPONSE_RESULT_ITEM_ALREADY_OWNED, 7);
define(BILLING_RESPONSE_RESULT_ITEM_NOT_OWNED, 8);

function fnEncrypt($message, $initialVector, $secretKey) {
    return base64_encode(
                    mcrypt_encrypt(
                            MCRYPT_RIJNDAEL_128, md5($secretKey), $message, MCRYPT_MODE_CFB, $initialVector
                    )
    );
}

function verifySignatureTransaction($signed_data, $signature, $public_key_base64) {
    $key = "-----BEGIN PUBLIC KEY-----\n" .
            chunk_split($public_key_base64, 64, "\n") .
            '-----END PUBLIC KEY-----';
    $key = openssl_pkey_get_public($key);
    if ($key === false) {
        die("Public key not valid");
    }
    $signature = base64_decode($signature);
    $result = openssl_verify(
            $signed_data, $signature, $key, OPENSSL_ALGO_SHA1
    );

    if (0 === $result) {
        return false;
    } else {
        if (1 !== $result) {
            return false;
        } else {
            return true;
        }
    }
}
//$responseData='{"orderId": "Qda85m87jnSV8Pex", "purchaseToken": "Qda85m87jnSV8Pex", "developerPayload": "ajab rasmi shodeha", "packageName": "com.raianraika.magic", "purchaseState": 0, "purchaseTime": 1394041928813, "productId": "666"}';
//$signature='NiNXZJqvtThtpumxo9VGf5oiEfR08360HZQbAhZkFWweb6InrSauV8RULTtOM  3mpFx1HodEssMTjno0Dc0UJ8N1CQwS94XHl4qQpx5IoLCDbSmhHd82QPYbMIe2dwUsSo19y6S4NU2tDgro BuADiRR24pgXzAvcZjTlByUpvJApe8hWCApiGVwrQpXpa0J87D0SCJUapWwSdC5FFLnOSPMQopAhWp/YbzqMZW';

?>