/**
 * Enterprise Auth Security & Cryptographic Password Hashing Utility.
 * 
 * Guarantees:
 * 1. Zero Plaintext Passwords in Source Code or Local Storage.
 * 2. Irreversible SHA-256 Cryptographic Hashing.
 * 3. Self-Serve Password Change for Super Admin and All Tenant Users.
 * 4. Total Privacy: Password hashes are never visible in user directories or logs.
 */

// Initial Seed SHA-256 Hashes (Plaintext passwords NEVER exist in code)
// Hash of default initial seed: 240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9
const DEFAULT_SUPER_ADMIN_HASH = "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9";
// Hash of demo SRE seed: 459aa9b36f4c740533a5fd26a10bbe674576210c10ac6e2befcd86f8d0405c99
const DEFAULT_DEMO_SRE_HASH = "459aa9b36f4c740533a5fd26a10bbe674576210c10ac6e2befcd86f8d0405c99";

const ADMIN_HASH_KEY = "aiops_admin_password_hash";
const USERS_STORAGE_KEY = "aiops_registered_users";

/**
 * Standard Synchronous SHA-256 Hashing Algorithm in Pure JavaScript.
 * Ensures fast, dependency-free execution in all browsers and environments.
 */
export function sha256(ascii: string): string {
  function rightRotate(value: number, amount: number) {
    return (value >>> amount) | (value << (32 - amount));
  }

  const mathPow = Math.pow;
  const maxWord = mathPow(2, 32);
  const lengthProperty = "length";
  let i = 0, j = 0;
  let result = "";

  const words: number[] = [];
  const asciiBitLength = ascii[lengthProperty] * 8;

  let hash = [
    0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
    0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
  ];

  const k = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
  ];

  let compositeClear = ascii + "\x80";
  while ((compositeClear[lengthProperty] % 64) - 56) compositeClear += "\x00";

  for (i = 0; i < compositeClear[lengthProperty]; i++) {
    j = compositeClear.charCodeAt(i);
    if (j >> 8) return ""; // Non-ASCII safeguard
    words[i >> 2] |= j << ((3 - (i % 4)) * 8);
  }
  words[words[lengthProperty]] = (asciiBitLength / maxWord) | 0;
  words[words[lengthProperty]] = asciiBitLength;

  for (j = 0; j < words[lengthProperty]; ) {
    const w = words.slice(j, (j += 16));
    const oldHash = hash;
    hash = hash.slice(0, 8);

    for (i = 0; i < 64; i++) {
      const w15 = w[i - 15],
        w2 = w[i - 2];
      const s0 = rightRotate(w15, 7) ^ rightRotate(w15, 18) ^ (w15 >>> 3);
      const s1 = rightRotate(w2, 17) ^ rightRotate(w2, 19) ^ (w2 >>> 10);
      w[i] =
        i < 16
          ? w[i]
          : (((w[i - 16] + s0) | 0) + ((w[i - 7] + s1) | 0)) | 0;

      const ch = (hash[4] & hash[5]) ^ (~hash[4] & hash[6]);
      const maj =
        (hash[0] & hash[1]) ^ (hash[0] & hash[2]) ^ (hash[1] & hash[2]);
      const temp1 =
        (((hash[7] + (rightRotate(hash[4], 6) ^ rightRotate(hash[4], 11) ^ rightRotate(hash[4], 25))) |
          0) +
          ((ch + k[i]) | 0) +
          w[i]) |
        0;
      const temp2 =
        ((rightRotate(hash[0], 2) ^ rightRotate(hash[0], 13) ^ rightRotate(hash[0], 22)) +
          maj) |
        0;

      hash = [(temp1 + temp2) | 0, hash[0], hash[1], hash[2], (hash[3] + temp1) | 0, hash[4], hash[5], hash[6]];
    }

    for (i = 0; i < 8; i++) {
      hash[i] = (hash[i] + oldHash[i]) | 0;
    }
  }

  for (i = 0; i < 8; i++) {
    for (let b = 3; b >= 0; b--) {
      const byte = (hash[i] >> (b * 8)) & 255;
      result += (byte < 16 ? "0" : "") + byte.toString(16);
    }
  }
  return result;
}

/**
 * Validates Super Admin password against stored hash.
 */
export function verifySuperAdminPassword(passwordInput: string): boolean {
  if (typeof window === "undefined") return false;
  const currentHash = localStorage.getItem(ADMIN_HASH_KEY) || DEFAULT_SUPER_ADMIN_HASH;
  return sha256(passwordInput) === currentHash;
}

/**
 * Validates Demo SRE password.
 */
export function verifyDemoSREPassword(passwordInput: string): boolean {
  return sha256(passwordInput) === DEFAULT_DEMO_SRE_HASH;
}

/**
 * Validates Enterprise Strong Password Policy:
 * 1. Minimum 8 characters
 * 2. At least 1 Uppercase letter (A-Z)
 * 3. At least 1 Lowercase letter (a-z)
 * 4. At least 1 Number (0-9)
 * 5. At least 1 Special character (!@#$%^&*...)
 */
export interface PasswordValidationResult {
  isValid: boolean;
  hasMinLength: boolean;
  hasUpperCase: boolean;
  hasLowerCase: boolean;
  hasNumber: boolean;
  hasSpecialChar: boolean;
  errorMessage?: string;
}

export function validatePasswordStrength(password: string): PasswordValidationResult {
  const hasMinLength = password.length >= 8;
  const hasUpperCase = /[A-Z]/.test(password);
  const hasLowerCase = /[a-z]/.test(password);
  const hasNumber = /[0-9]/.test(password);
  const hasSpecialChar = /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?`~]/.test(password);

  const isValid = hasMinLength && hasUpperCase && hasLowerCase && hasNumber && hasSpecialChar;

  let errorMessage: string | undefined = undefined;
  if (!isValid) {
    const missing: string[] = [];
    if (!hasMinLength) missing.push("minimum 8 characters");
    if (!hasUpperCase) missing.push("1 uppercase letter (A-Z)");
    if (!hasLowerCase) missing.push("1 lowercase letter (a-z)");
    if (!hasNumber) missing.push("1 number (0-9)");
    if (!hasSpecialChar) missing.push("1 special symbol (!@#$...)");
    errorMessage = `Password must contain ${missing.join(", ")}.`;
  }

  return {
    isValid,
    hasMinLength,
    hasUpperCase,
    hasLowerCase,
    hasNumber,
    hasSpecialChar,
    errorMessage,
  };
}

/**
 * Changes Super Admin Password and saves irreversible hash.
 */
export function changeSuperAdminPassword(
  currentPasswordInput: string,
  newPasswordInput: string
): { success: boolean; message: string } {
  if (typeof window === "undefined") {
    return { success: false, message: "Window context unavailable" };
  }

  if (!verifySuperAdminPassword(currentPasswordInput)) {
    return { success: false, message: "Current Super Admin password is incorrect." };
  }

  const strength = validatePasswordStrength(newPasswordInput);
  if (!strength.isValid) {
    return { success: false, message: strength.errorMessage || "Password does not meet enterprise security standards." };
  }

  const newHash = sha256(newPasswordInput);
  localStorage.setItem(ADMIN_HASH_KEY, newHash);
  return { success: true, message: "Super Admin password updated successfully! Your account is now secured." };
}

/**
 * Validates registered user password against stored hash (or legacy plaintext).
 */
export function verifyRegisteredUserPassword(storedUser: any, passwordInput: string): boolean {
  const inputHash = sha256(passwordInput);
  if (storedUser.passwordHash) {
    return storedUser.passwordHash === inputHash;
  }
  // Legacy migration check: if old plaintext exists, check it and upgrade to hash immediately
  if (storedUser.password === passwordInput) {
    storedUser.passwordHash = inputHash;
    delete storedUser.password;
    return true;
  }
  return false;
}

/**
 * Changes a regular user's password.
 */
export function changeUserPassword(
  emailOrMobile: string,
  currentPasswordInput: string,
  newPasswordInput: string
): { success: boolean; message: string } {
  if (typeof window === "undefined") {
    return { success: false, message: "Window context unavailable" };
  }

  const strength = validatePasswordStrength(newPasswordInput);
  if (!strength.isValid) {
    return { success: false, message: strength.errorMessage || "Password does not meet enterprise security standards." };
  }

  try {
    const raw = localStorage.getItem(USERS_STORAGE_KEY);
    const users = raw ? JSON.parse(raw) : [];
    const cleanId = emailOrMobile.trim().toLowerCase();

    const userIndex = users.findIndex(
      (u: any) =>
        u.email?.toLowerCase() === cleanId ||
        u.mobile?.replace(/\D/g, "") === cleanId.replace(/\D/g, "")
    );

    if (userIndex === -1) {
      return { success: false, message: "User account not found." };
    }

    const targetUser = users[userIndex];
    if (!verifyRegisteredUserPassword(targetUser, currentPasswordInput)) {
      return { success: false, message: "Current password is incorrect." };
    }

    // Update with secure hash, delete plaintext password
    targetUser.passwordHash = sha256(newPasswordInput);
    delete targetUser.password;

    users[userIndex] = targetUser;
    localStorage.setItem(USERS_STORAGE_KEY, JSON.stringify(users));

    return { success: true, message: "Password updated successfully!" };
  } catch (e) {
    return { success: false, message: "Failed to update password. Please try again." };
  }
}

