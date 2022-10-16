document.getElementById('formRavencoinAddress').addEventListener("change",sha256);
document.getElementById('formPgpPubkey').addEventListener("change",sha256);
document.getElementById('formSignature').addEventListener("change",sha256);


async function sha256() {
  var field1 = document.getElementById('formRavencoinAddress').value;
  var field2 = document.getElementById('formPgpPubkey').value;
  var signature = document.getElementById('formSignature').value;
    if(field1 != "" && field2 != ""){
      var jsonString = '"tag_type": "AET","ravencoin_address": "'+field1+'","pgp_pubkey": "'+field2+'"';

      document.getElementById('jsonString').value = jsonString;
      console.log(jsonString);
      // encode as UTF-8
      const msgBuffer = new TextEncoder('utf-8').encode(jsonString);

      // hash the message
      const hashBuffer = await window.crypto.subtle.digest('SHA-256', msgBuffer);

      // convert ArrayBuffer to Array
      const hashArray = Array.from(new Uint8Array(hashBuffer));

      // convert bytes to hex string
      const hashHex = hashArray.map(b => ('00' + b.toString(16)).slice(-2)).join('');
      console.log(hashHex);
      document.getElementById('sha256').value = hashHex;

      document.getElementById('fullJson').value = "{\"tag\": {\"tag_type\": \"AET,\"ravencoin_address\": \""+field1+"\",\"pgp_pubkey\": \""+field2+"\"},\"metadata_signature\": {\"signature_hash\": \""+hashHex+"\",\"signature\": \""+signature+"\"}}";
    }
}
