import { initializeApp, getApps } from "firebase/app";
import {
  getAuth,
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
} from "firebase/auth";
import {
  getFirestore,
  collection,
  addDoc,
  doc,
  updateDoc,
  deleteDoc,
  query,
  orderBy,
  onSnapshot,
  serverTimestamp,
} from "firebase/firestore";

const firebaseConfig = {
  apiKey: "AIzaSyAshJV9t1XkvmX1s9nWMXu0VXkJHYKzjLU",
  authDomain: "sanrajllp.firebaseapp.com",
  projectId: "sanrajllp",
  storageBucket: "sanrajllp.firebasestorage.app",
  messagingSenderId: "493927465948",
  appId: "1:493927465948:web:2697c06f475f6d7b3d4519",
  measurementId: "G-3EQ9R30K4S",
};

const app = getApps().length ? getApps()[0] : initializeApp(firebaseConfig);

export const auth = getAuth(app);
export const db = getFirestore(app);

export {
  signInWithEmailAndPassword,
  signOut,
  onAuthStateChanged,
  collection,
  addDoc,
  doc,
  updateDoc,
  deleteDoc,
  query,
  orderBy,
  onSnapshot,
  serverTimestamp,
};
