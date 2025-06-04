export async function importPrivateKey(pem) {
  try {
    console.log("Importando clave privada...");
    const key = pem.replace(/-----.*?-----/g, "").replace(/\s/g, "");
    const binaryDer = Uint8Array.from(atob(key), c => c.charCodeAt(0));
    const privKey = await crypto.subtle.importKey(
      "pkcs8",
      binaryDer.buffer,
      { name: "ECDH", namedCurve: "P-256" },
      false,
      ["deriveBits"]
    );
    console.log("Clave privada importada con éxito.");
    return privKey;
  } catch (e) {
    console.error("Error importando clave privada:", e);
    throw e;
  }
}

export async function importPublicKey(pem) {
  try {
    console.log("Importando clave pública efímera...");
    const key = pem.replace(/-----.*?-----/g, "").replace(/\s/g, "");
    const binaryDer = Uint8Array.from(atob(key), c => c.charCodeAt(0));
    const pubKey = await crypto.subtle.importKey(
      "spki",
      binaryDer.buffer,
      { name: "ECDH", namedCurve: "P-256" },
      false,
      []
    );
    console.log("Clave pública efímera importada con éxito.");
    return pubKey;
  } catch (e) {
    console.error("Error importando clave pública efímera:", e);
    throw e;
  }
}

async function deriveSharedBits(privateKey, publicKey) {
  try {
    console.log("Derivando bits compartidos...");
    const bits = await crypto.subtle.deriveBits(
      {
        name: "ECDH",
        public: publicKey,
      },
      privateKey,
      256
    );
    console.log("Bits compartidos derivados con éxito.");
    return bits;
  } catch (e) {
    console.error("Error derivando bits compartidos:", e);
    throw e;
  }
}

async function hkdfSha256(ikm, info = "ecies") {
  try {
    console.log("Ejecutando HKDF...");
    const enc = new TextEncoder();
    const hmacKey = await crypto.subtle.importKey(
      "raw",
      new Uint8Array(32), // salt vacío
      { name: "HMAC", hash: "SHA-256" },
      false,
      ["sign"]
    );

    const prk = await crypto.subtle.sign("HMAC", hmacKey, ikm);

    const prkKey = await crypto.subtle.importKey(
      "raw",
      prk,
      { name: "HMAC", hash: "SHA-256" },
      false,
      ["sign"]
    );

    const infoBuffer = enc.encode(info);
    const hkdfInput = new Uint8Array([...infoBuffer, 0x01]);
    const okm = await crypto.subtle.sign("HMAC", prkKey, hkdfInput);
    console.log("HKDF completado con éxito.");
    return okm;
  } catch (e) {
    console.error("Error ejecutando HKDF:", e);
    throw e;
  }
}

export async function deriveSharedKey(privateKey, publicKey) {
  try {
    console.log("Derivando clave compartida...");
    const sharedBits = await deriveSharedBits(privateKey, publicKey);
    const hkdfOutput = await hkdfSha256(sharedBits);
    const key = await crypto.subtle.importKey(
      "raw",
      hkdfOutput,
      { name: "AES-GCM" },
      false,
      ["decrypt"]
    );
    console.log("Clave compartida derivada e importada con éxito.");
    return key;
  } catch (e) {
    console.error("Error derivando clave compartida:", e);
    throw e;
  }
}

export async function decryptMessage(ciphertextBase64, nonceBase64, aesKey) {
  try {
    console.log("Descifrando mensaje AES-GCM...");
    const ciphertext = Uint8Array.from(atob(ciphertextBase64), c => c.charCodeAt(0));
    const nonce = Uint8Array.from(atob(nonceBase64), c => c.charCodeAt(0));

    const decrypted = await crypto.subtle.decrypt(
      {
        name: "AES-GCM",
        iv: nonce,
      },
      aesKey,
      ciphertext
    );

    console.log("Mensaje descifrado con éxito.");
    return new TextDecoder().decode(decrypted);
  } catch (e) {
    console.error("Error descifrando mensaje AES-GCM:", e);
    throw e;
  }
}

export async function descifrarTodo(claveCifrada, contenido, clavePrivadaPem) {
  try {
    console.log("Iniciando proceso completo de descifrado...");
    const privateKey = await importPrivateKey(clavePrivadaPem);
    const publicKeyEphemeral = await importPublicKey(claveCifrada.ephemeral_public_key);

    const derivedKey = await deriveSharedKey(privateKey, publicKeyEphemeral);

    const encryptedKey = Uint8Array.from(atob(claveCifrada.encrypted_key), c => c.charCodeAt(0));
    const nonceKey = Uint8Array.from(atob(claveCifrada.nonce), c => c.charCodeAt(0));

    console.log("Descifrando clave AES...");
    const aesKeyBuffer = await window.crypto.subtle.decrypt(
      { name: "AES-GCM", iv: nonceKey },
      derivedKey,
      encryptedKey
    );
    console.log("Clave AES descifrada con éxito.");

    const aesKey = await window.crypto.subtle.importKey(
      "raw",
      aesKeyBuffer,
      { name: "AES-GCM" },
      false,
      ["decrypt"]
    );

    const textoPlano = await decryptMessage(contenido.ciphertext, contenido.nonce, aesKey);

    console.log("Proceso completo de descifrado finalizado.");
    return textoPlano;
  } catch (e) {
    console.error("Error en descifrarTodo:", e);
    throw e;
  }
}
