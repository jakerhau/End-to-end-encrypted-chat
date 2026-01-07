/**
 * Performance Tests for E2EE Crypto Functions
 * 
 * Đo lường hiệu năng các thao tác mã hóa
 */

import { describe, it, expect } from 'vitest';
import {
    generateRSAKeyPair,
    generateAESKey,
    aesEncrypt,
    aesDecrypt,
    encryptSessionKey,
    decryptSessionKey,
    generateFingerprint,
    exportPublicKey,
    deriveKeyFromPIN,
    generateSalt,
} from '@/lib/crypto';


// Helper function to measure execution time
async function measureTime(fn: () => Promise<void>): Promise<number> {
    const start = performance.now();
    await fn();
    const end = performance.now();
    return end - start;
}


// ==================== RSA Performance ====================

describe('PT-CRYPTO-001: RSA Key Generation Performance', () => {
    it('should generate 10 RSA key pairs in under 5 seconds', async () => {
        const times: number[] = [];
        
        for (let i = 0; i < 10; i++) {
            const time = await measureTime(async () => {
                await generateRSAKeyPair();
            });
            times.push(time);
        }
        
        const totalTime = times.reduce((a, b) => a + b, 0);
        const avgTime = totalTime / times.length;
        
        console.log(`RSA Key Generation:`);
        console.log(`  Total (10 keys): ${totalTime.toFixed(2)}ms`);
        console.log(`  Average: ${avgTime.toFixed(2)}ms per key`);
        
        expect(totalTime).toBeLessThan(5000); // Under 5 seconds
    });
});


// ==================== AES Performance ====================

describe('PT-CRYPTO-002: AES Encryption Performance', () => {
    it('should encrypt 100 messages in under 1 second', async () => {
        const aesKey = await generateAESKey();
        const message = 'A'.repeat(1000); // 1KB message
        const times: number[] = [];
        
        for (let i = 0; i < 100; i++) {
            const time = await measureTime(async () => {
                await aesEncrypt(message, aesKey);
            });
            times.push(time);
        }
        
        const totalTime = times.reduce((a, b) => a + b, 0);
        const avgTime = totalTime / times.length;
        
        console.log(`AES Encryption (1KB messages):`);
        console.log(`  Total (100 messages): ${totalTime.toFixed(2)}ms`);
        console.log(`  Average: ${avgTime.toFixed(2)}ms per message`);
        console.log(`  Throughput: ${(100000 / totalTime).toFixed(2)} messages/second`);
        
        expect(totalTime).toBeLessThan(1000); // Under 1 second
    });

    it('should decrypt 100 messages in under 1 second', async () => {
        const aesKey = await generateAESKey();
        const message = 'A'.repeat(1000);
        
        // Pre-encrypt messages
        const encryptedMessages: string[] = [];
        for (let i = 0; i < 100; i++) {
            encryptedMessages.push(await aesEncrypt(message, aesKey));
        }
        
        const times: number[] = [];
        for (const encrypted of encryptedMessages) {
            const time = await measureTime(async () => {
                await aesDecrypt(encrypted, aesKey);
            });
            times.push(time);
        }
        
        const totalTime = times.reduce((a, b) => a + b, 0);
        const avgTime = totalTime / times.length;
        
        console.log(`AES Decryption (1KB messages):`);
        console.log(`  Total (100 messages): ${totalTime.toFixed(2)}ms`);
        console.log(`  Average: ${avgTime.toFixed(2)}ms per message`);
        console.log(`  Throughput: ${(100000 / totalTime).toFixed(2)} messages/second`);
        
        expect(totalTime).toBeLessThan(1000);
    });

    it('should handle large messages (10KB) efficiently', async () => {
        const aesKey = await generateAESKey();
        const largeMessage = 'A'.repeat(10000); // 10KB
        
        const encryptTime = await measureTime(async () => {
            await aesEncrypt(largeMessage, aesKey);
        });
        
        const encrypted = await aesEncrypt(largeMessage, aesKey);
        
        const decryptTime = await measureTime(async () => {
            await aesDecrypt(encrypted, aesKey);
        });
        
        console.log(`Large Message (10KB):`);
        console.log(`  Encrypt: ${encryptTime.toFixed(2)}ms`);
        console.log(`  Decrypt: ${decryptTime.toFixed(2)}ms`);
        
        expect(encryptTime).toBeLessThan(100);
        expect(decryptTime).toBeLessThan(100);
    });
});


// ==================== Session Key Exchange Performance ====================

describe('PT-CRYPTO-003: Session Key Exchange Performance', () => {
    it('should exchange 50 session keys in under 3 seconds', async () => {
        const rsaKeyPair = await generateRSAKeyPair();
        const times: number[] = [];
        
        for (let i = 0; i < 50; i++) {
            const aesKey = await generateAESKey();
            
            const time = await measureTime(async () => {
                const encrypted = await encryptSessionKey(aesKey, rsaKeyPair.publicKey);
                await decryptSessionKey(encrypted, rsaKeyPair.privateKey);
            });
            times.push(time);
        }
        
        const totalTime = times.reduce((a, b) => a + b, 0);
        const avgTime = totalTime / times.length;
        
        console.log(`Session Key Exchange:`);
        console.log(`  Total (50 exchanges): ${totalTime.toFixed(2)}ms`);
        console.log(`  Average: ${avgTime.toFixed(2)}ms per exchange`);
        
        expect(totalTime).toBeLessThan(3000);
    });
});


// ==================== PBKDF2 Performance ====================

describe('PT-CRYPTO-004: PBKDF2 Key Derivation Performance', () => {
    it('should derive key in under 500ms (100k iterations)', async () => {
        const pin = '123456';
        const salt = generateSalt();
        
        const time = await measureTime(async () => {
            await deriveKeyFromPIN(pin, salt, 100000);
        });
        
        console.log(`PBKDF2 Key Derivation (100k iterations):`);
        console.log(`  Time: ${time.toFixed(2)}ms`);
        
        expect(time).toBeLessThan(500);
    });
});


// ==================== Fingerprint Performance ====================

describe('PT-CRYPTO-005: Fingerprint Generation Performance', () => {
    it('should generate 20 fingerprints efficiently', async () => {
        // Generate keys first (reduced from 100 to 20 for faster test)
        const publicKeys: string[] = [];
        for (let i = 0; i < 20; i++) {
            const keyPair = await generateRSAKeyPair();
            publicKeys.push(await exportPublicKey(keyPair.publicKey));
        }
        
        const times: number[] = [];
        for (const pubKey of publicKeys) {
            const time = await measureTime(async () => {
                await generateFingerprint(pubKey);
            });
            times.push(time);
        }
        
        const totalTime = times.reduce((a, b) => a + b, 0);
        const avgTime = totalTime / times.length;
        
        console.log(`Fingerprint Generation:`);
        console.log(`  Total (20 fingerprints): ${totalTime.toFixed(2)}ms`);
        console.log(`  Average: ${avgTime.toFixed(2)}ms per fingerprint`);
        
        expect(totalTime).toBeLessThan(1000); // Under 1 second for 20
    }, 30000); // 30 second timeout
});


// ==================== Concurrent Operations ====================

describe('PT-CRYPTO-006: Concurrent Crypto Operations', () => {
    it('should handle 20 concurrent encryptions', async () => {
        const aesKey = await generateAESKey();
        const messages = Array(20).fill('Concurrent test message');
        
        const start = performance.now();
        
        await Promise.all(
            messages.map(msg => aesEncrypt(msg, aesKey))
        );
        
        const totalTime = performance.now() - start;
        
        console.log(`Concurrent Encryption (20 parallel):`);
        console.log(`  Total time: ${totalTime.toFixed(2)}ms`);
        console.log(`  Per operation: ${(totalTime / 20).toFixed(2)}ms`);
        
        expect(totalTime).toBeLessThan(500);
    });
});
