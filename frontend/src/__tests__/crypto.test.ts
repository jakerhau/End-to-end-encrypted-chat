/**
 * Unit Tests for E2EE Crypto Functions
 * 
 * These tests cover the core cryptographic operations used in E2EE:
 * - RSA key generation
 * - AES encryption/decryption
 * - RSA encryption/decryption  
 * - RSA signing/verification
 * - Key derivation (PBKDF2)
 * - Fingerprint generation
 */

import { describe, it, expect } from 'vitest';
import {
    generateRSAKeyPair,
    exportPublicKey,
    exportPrivateKey,
    importPublicKey,
    importPrivateKey,
    generateAESKey,
    exportAESKey,
    importAESKey,
    aesEncrypt,
    aesDecrypt,
    generateFingerprint,
    formatFingerprint,
    encryptSessionKey,
    decryptSessionKey,
    arrayBufferToBase64,
    base64ToArrayBuffer,
    stringToArrayBuffer,
    arrayBufferToString,
    deriveKeyFromPIN,
    generateSalt,
    encryptPrivateKeyWithPIN,
    decryptPrivateKeyWithPIN,
    importPrivateKeyForSigning,
    importPublicKeyForVerifying,
    rsaSign,
    rsaVerify,
} from '@/lib/crypto';


// ==================== RSA KEY GENERATION ====================

describe('UT-CRYPTO-001: RSA Key Generation', () => {
    it('should generate valid RSA-2048 key pair', async () => {
        const keyPair = await generateRSAKeyPair();
        
        expect(keyPair).toBeDefined();
        expect(keyPair.publicKey).toBeDefined();
        expect(keyPair.privateKey).toBeDefined();
        expect(keyPair.publicKey.type).toBe('public');
        expect(keyPair.privateKey.type).toBe('private');
    });

    it('should generate unique key pairs each time', async () => {
        const keyPair1 = await generateRSAKeyPair();
        const keyPair2 = await generateRSAKeyPair();
        
        const pub1 = await exportPublicKey(keyPair1.publicKey);
        const pub2 = await exportPublicKey(keyPair2.publicKey);
        
        expect(pub1).not.toBe(pub2);
    });

    it('should export public key to SPKI format (Base64)', async () => {
        const keyPair = await generateRSAKeyPair();
        const exported = await exportPublicKey(keyPair.publicKey);
        
        expect(typeof exported).toBe('string');
        expect(exported.length).toBeGreaterThan(100); // RSA-2048 public key is ~392 chars
    });

    it('should export private key to PKCS8 format (Base64)', async () => {
        const keyPair = await generateRSAKeyPair();
        const exported = await exportPrivateKey(keyPair.privateKey);
        
        expect(typeof exported).toBe('string');
        expect(exported.length).toBeGreaterThan(1000); // RSA-2048 private key is ~1680 chars
    });

    it('should import public key from Base64', async () => {
        const keyPair = await generateRSAKeyPair();
        const exported = await exportPublicKey(keyPair.publicKey);
        
        const imported = await importPublicKey(exported);
        
        expect(imported).toBeDefined();
        expect(imported.type).toBe('public');
    });

    it('should import private key from Base64', async () => {
        const keyPair = await generateRSAKeyPair();
        const exported = await exportPrivateKey(keyPair.privateKey);
        
        const imported = await importPrivateKey(exported);
        
        expect(imported).toBeDefined();
        expect(imported.type).toBe('private');
    });
});


// ==================== AES KEY GENERATION ====================

describe('UT-CRYPTO-002: AES Key Generation', () => {
    it('should generate valid AES-256 key', async () => {
        const aesKey = await generateAESKey();
        
        expect(aesKey).toBeDefined();
        expect(aesKey.type).toBe('secret');
    });

    it('should generate unique AES keys each time', async () => {
        const key1 = await generateAESKey();
        const key2 = await generateAESKey();
        
        const raw1 = await exportAESKey(key1);
        const raw2 = await exportAESKey(key2);
        
        const base64_1 = arrayBufferToBase64(raw1);
        const base64_2 = arrayBufferToBase64(raw2);
        
        expect(base64_1).not.toBe(base64_2);
    });

    it('should export AES key to 32 bytes (256-bit)', async () => {
        const aesKey = await generateAESKey();
        const exported = await exportAESKey(aesKey);
        
        expect(exported.byteLength).toBe(32);
    });

    it('should import AES key from raw bytes', async () => {
        const aesKey = await generateAESKey();
        const exported = await exportAESKey(aesKey);
        
        const imported = await importAESKey(exported);
        
        expect(imported).toBeDefined();
        expect(imported.type).toBe('secret');
    });
});


// ==================== AES ENCRYPTION/DECRYPTION ====================

describe('UT-CRYPTO-003: AES Encryption/Decryption', () => {
    it('should encrypt and decrypt message correctly', async () => {
        const aesKey = await generateAESKey();
        const plaintext = 'Hello, E2EE World! 🔐';
        
        const encrypted = await aesEncrypt(plaintext, aesKey);
        const decrypted = await aesDecrypt(encrypted, aesKey);
        
        expect(decrypted).toBe(plaintext);
    });

    it('should produce different ciphertexts for same plaintext (random IV)', async () => {
        const aesKey = await generateAESKey();
        const plaintext = 'Same message';
        
        const encrypted1 = await aesEncrypt(plaintext, aesKey);
        const encrypted2 = await aesEncrypt(plaintext, aesKey);
        
        expect(encrypted1).not.toBe(encrypted2);
    });

    it('should fail decryption with wrong key', async () => {
        const aesKey1 = await generateAESKey();
        const aesKey2 = await generateAESKey();
        const plaintext = 'Secret message';
        
        const encrypted = await aesEncrypt(plaintext, aesKey1);
        const decrypted = await aesDecrypt(encrypted, aesKey2);
        
        expect(decrypted).toBeNull();
    });

    it('should handle empty string', async () => {
        const aesKey = await generateAESKey();
        const plaintext = '';
        
        const encrypted = await aesEncrypt(plaintext, aesKey);
        const decrypted = await aesDecrypt(encrypted, aesKey);
        
        expect(decrypted).toBe(plaintext);
    });

    it('should handle unicode characters', async () => {
        const aesKey = await generateAESKey();
        const plaintext = '你好世界 🌍 مرحبا';
        
        const encrypted = await aesEncrypt(plaintext, aesKey);
        const decrypted = await aesDecrypt(encrypted, aesKey);
        
        expect(decrypted).toBe(plaintext);
    });

    it('should handle long messages', async () => {
        const aesKey = await generateAESKey();
        const plaintext = 'A'.repeat(10000);
        
        const encrypted = await aesEncrypt(plaintext, aesKey);
        const decrypted = await aesDecrypt(encrypted, aesKey);
        
        expect(decrypted).toBe(plaintext);
    });

    it('should support Additional Authenticated Data (AAD)', async () => {
        const aesKey = await generateAESKey();
        const plaintext = 'Message with AAD';
        const aad = stringToArrayBuffer('context-data');
        
        const encrypted = await aesEncrypt(plaintext, aesKey, aad);
        const decrypted = await aesDecrypt(encrypted, aesKey, undefined, aad);
        
        expect(decrypted).toBe(plaintext);
    });

    it('should fail decryption with wrong AAD', async () => {
        const aesKey = await generateAESKey();
        const plaintext = 'Message with AAD';
        const aad1 = stringToArrayBuffer('context-1');
        const aad2 = stringToArrayBuffer('context-2');
        
        const encrypted = await aesEncrypt(plaintext, aesKey, aad1);
        const decrypted = await aesDecrypt(encrypted, aesKey, undefined, aad2);
        
        expect(decrypted).toBeNull();
    });
});


// ==================== RSA ENCRYPTION/DECRYPTION ====================

describe('UT-CRYPTO-004: RSA Encryption/Decryption (Session Key Exchange)', () => {
    it('should encrypt and decrypt session key correctly', async () => {
        const rsaKeyPair = await generateRSAKeyPair();
        const aesKey = await generateAESKey();
        
        const encrypted = await encryptSessionKey(aesKey, rsaKeyPair.publicKey);
        const decrypted = await decryptSessionKey(encrypted, rsaKeyPair.privateKey);
        
        // Compare the raw bytes
        const original = await exportAESKey(aesKey);
        const recovered = await exportAESKey(decrypted);
        
        expect(arrayBufferToBase64(original)).toBe(arrayBufferToBase64(recovered));
    });

    it('should fail decryption with wrong private key', async () => {
        const rsaKeyPair1 = await generateRSAKeyPair();
        const rsaKeyPair2 = await generateRSAKeyPair();
        const aesKey = await generateAESKey();
        
        const encrypted = await encryptSessionKey(aesKey, rsaKeyPair1.publicKey);
        
        await expect(
            decryptSessionKey(encrypted, rsaKeyPair2.privateKey)
        ).rejects.toThrow();
    });
});


// ==================== RSA SIGNING/VERIFYING ====================

describe('UT-CRYPTO-005: RSA Signing/Verification', () => {
    it('should sign and verify data correctly', async () => {
        const rsaKeyPair = await generateRSAKeyPair();
        const privateKeyBase64 = await exportPrivateKey(rsaKeyPair.privateKey);
        const publicKeyBase64 = await exportPublicKey(rsaKeyPair.publicKey);
        
        // Import keys for signing/verifying (RSA-PSS)
        const signingKey = await importPrivateKeyForSigning(privateKeyBase64);
        const verifyingKey = await importPublicKeyForVerifying(publicKeyBase64);
        
        const data = stringToArrayBuffer('Data to sign');
        
        const signature = await rsaSign(data, signingKey);
        const isValid = await rsaVerify(signature, data, verifyingKey);
        
        expect(isValid).toBe(true);
    });

    it('should fail verification with tampered data', async () => {
        const rsaKeyPair = await generateRSAKeyPair();
        const privateKeyBase64 = await exportPrivateKey(rsaKeyPair.privateKey);
        const publicKeyBase64 = await exportPublicKey(rsaKeyPair.publicKey);
        
        const signingKey = await importPrivateKeyForSigning(privateKeyBase64);
        const verifyingKey = await importPublicKeyForVerifying(publicKeyBase64);
        
        const originalData = stringToArrayBuffer('Original data');
        const tamperedData = stringToArrayBuffer('Tampered data');
        
        const signature = await rsaSign(originalData, signingKey);
        const isValid = await rsaVerify(signature, tamperedData, verifyingKey);
        
        expect(isValid).toBe(false);
    });

    it('should fail verification with wrong public key', async () => {
        const rsaKeyPair1 = await generateRSAKeyPair();
        const rsaKeyPair2 = await generateRSAKeyPair();
        
        const privateKeyBase64 = await exportPrivateKey(rsaKeyPair1.privateKey);
        const publicKeyBase64 = await exportPublicKey(rsaKeyPair2.publicKey); // Wrong key
        
        const signingKey = await importPrivateKeyForSigning(privateKeyBase64);
        const verifyingKey = await importPublicKeyForVerifying(publicKeyBase64);
        
        const data = stringToArrayBuffer('Data to sign');
        
        const signature = await rsaSign(data, signingKey);
        const isValid = await rsaVerify(signature, data, verifyingKey);
        
        expect(isValid).toBe(false);
    });
});


// ==================== KEY DERIVATION (PBKDF2) ====================

describe('UT-CRYPTO-006: PBKDF2 Key Derivation', () => {
    it('should derive key from PIN', async () => {
        const pin = '123456';
        const salt = generateSalt();
        
        const derivedKey = await deriveKeyFromPIN(pin, salt);
        
        expect(derivedKey).toBeDefined();
        expect(derivedKey.type).toBe('secret');
    });

    it('should derive same key with same PIN and salt', async () => {
        const pin = '123456';
        const salt = generateSalt();
        
        const key1 = await deriveKeyFromPIN(pin, salt);
        const key2 = await deriveKeyFromPIN(pin, salt);
        
        // Export and compare
        const raw1 = await crypto.subtle.exportKey('raw', key1);
        const raw2 = await crypto.subtle.exportKey('raw', key2);
        
        expect(arrayBufferToBase64(raw1)).toBe(arrayBufferToBase64(raw2));
    });

    it('should derive different keys with different salts', async () => {
        const pin = '123456';
        const salt1 = generateSalt();
        const salt2 = generateSalt();
        
        const key1 = await deriveKeyFromPIN(pin, salt1);
        const key2 = await deriveKeyFromPIN(pin, salt2);
        
        const raw1 = await crypto.subtle.exportKey('raw', key1);
        const raw2 = await crypto.subtle.exportKey('raw', key2);
        
        expect(arrayBufferToBase64(raw1)).not.toBe(arrayBufferToBase64(raw2));
    });

    it('should generate 16-byte salt', () => {
        const salt = generateSalt();
        expect(salt.length).toBe(16);
    });
});


// ==================== PRIVATE KEY ENCRYPTION WITH PIN ====================

describe('UT-CRYPTO-007: Private Key Encryption with PIN', () => {
    it('should encrypt and decrypt private key with correct PIN', async () => {
        const rsaKeyPair = await generateRSAKeyPair();
        const privateKeyBase64 = await exportPrivateKey(rsaKeyPair.privateKey);
        const pin = 'mySecretPin123';
        
        const { encryptedPrivateKey, iv, salt } = await encryptPrivateKeyWithPIN(
            privateKeyBase64, 
            pin
        );
        
        const decrypted = await decryptPrivateKeyWithPIN(
            encryptedPrivateKey,
            pin,
            iv,
            salt
        );
        
        expect(decrypted).toBe(privateKeyBase64);
    });

    it('should fail decryption with wrong PIN', async () => {
        const rsaKeyPair = await generateRSAKeyPair();
        const privateKeyBase64 = await exportPrivateKey(rsaKeyPair.privateKey);
        const correctPin = 'correctPin';
        const wrongPin = 'wrongPin';
        
        const { encryptedPrivateKey, iv, salt } = await encryptPrivateKeyWithPIN(
            privateKeyBase64, 
            correctPin
        );
        
        const decrypted = await decryptPrivateKeyWithPIN(
            encryptedPrivateKey,
            wrongPin,
            iv,
            salt
        );
        
        expect(decrypted).toBeNull();
    });
});


// ==================== FINGERPRINT ====================

describe('UT-CRYPTO-008: Fingerprint Generation', () => {
    it('should generate fingerprint from public key', async () => {
        const rsaKeyPair = await generateRSAKeyPair();
        const publicKeyBase64 = await exportPublicKey(rsaKeyPair.publicKey);
        
        const fingerprint = await generateFingerprint(publicKeyBase64);
        
        expect(fingerprint).toBeDefined();
        expect(typeof fingerprint).toBe('string');
        expect(fingerprint.length).toBe(16); // First 16 hex chars
    });

    it('should generate same fingerprint for same key', async () => {
        const rsaKeyPair = await generateRSAKeyPair();
        const publicKeyBase64 = await exportPublicKey(rsaKeyPair.publicKey);
        
        const fp1 = await generateFingerprint(publicKeyBase64);
        const fp2 = await generateFingerprint(publicKeyBase64);
        
        expect(fp1).toBe(fp2);
    });

    it('should generate different fingerprints for different keys', async () => {
        const keyPair1 = await generateRSAKeyPair();
        const keyPair2 = await generateRSAKeyPair();
        
        const pub1 = await exportPublicKey(keyPair1.publicKey);
        const pub2 = await exportPublicKey(keyPair2.publicKey);
        
        const fp1 = await generateFingerprint(pub1);
        const fp2 = await generateFingerprint(pub2);
        
        expect(fp1).not.toBe(fp2);
    });

    it('should format fingerprint correctly', () => {
        const fingerprint = '1234567890abcdef';
        const formatted = formatFingerprint(fingerprint);
        
        expect(formatted).toBe('1234 5678 90ab cdef');
    });
});


// ==================== UTILITY FUNCTIONS ====================

describe('UT-CRYPTO-009: Utility Functions', () => {
    it('should convert ArrayBuffer to Base64 and back', () => {
        const original = new Uint8Array([1, 2, 3, 4, 5]);
        
        const base64 = arrayBufferToBase64(original.buffer);
        const recovered = new Uint8Array(base64ToArrayBuffer(base64));
        
        expect(recovered).toEqual(original);
    });

    it('should convert string to ArrayBuffer and back', () => {
        const original = 'Hello World 🌍';
        
        const buffer = stringToArrayBuffer(original);
        const recovered = arrayBufferToString(buffer);
        
        expect(recovered).toBe(original);
    });
});
