import "./styles.css";

const formRavencoinAddress = document.getElementById("form-ravencoinAddress");
const formPgpPubkey = document.getElementById("form-pgpPubkey");
const formSignatureHash = document.getElementById("form-signatureHash");
const formSignature = document.getElementById("form-signature");

let ravencoinAddressValue = "";
let phpPubkeyValue = "";

formRavencoinAddress.addEventListener("input", (event) => {
  console.log(event.target.value.trim());
  ravencoinAddressValue = event.target.value.trim();
  createSignatureHash();
});

formPgpPubkey.addEventListener("input", (event) => {
  console.log(event.target.value.trim());
  phpPubkeyValue = event.target.value.trim();
  createSignatureHash();
});

async function digestMessage(message) {
  const msgUint8 = new TextEncoder().encode(message);                           // encode as (utf-8) Uint8Array
  const hashBuffer = await crypto.subtle.digest('SHA-256', msgUint8);           // hash the message
  const hashArray = Array.from(new Uint8Array(hashBuffer));                     // convert buffer to byte array
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join(''); // convert bytes to hex string
  return hashHex;
}

function createSignatureHash() {
  // Do the hash creation
  console.log("ravencoinAddressValue", ravencoinAddressValue);
  console.log("phpPubkeyValue", phpPubkeyValue);
  const hashCalc = `"tag_type": "AET", "ravencoin_address": "${ravencoinAddressValue}", "pgp_pubkey": "${phpPubkeyValue}"`;

  digestMessage(hashCalc).then(digestHex => formSignatureHash.value = digestHex);

}
