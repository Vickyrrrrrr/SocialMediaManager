import { db } from '../config/firebase'
import { collection, addDoc, query, where, orderBy, onSnapshot, doc, getDoc } from 'firebase/firestore'
import { APP_ID } from '../config/constants'

/**
 * Save a design to Firestore
 */
export const saveDesign = async (userId, designData) => {
  try {
    const designDoc = {
      userId,
      prompt: designData.prompt,
      structuredNetlist: designData.structuredNetlist,
      fusionScript: designData.fusionScript,
      createdAt: new Date(),
      updatedAt: new Date(),
    }

    const docRef = await addDoc(
      collection(db, `artifacts/${APP_ID}/users/${userId}/ece_designs_fusion`),
      designDoc
    )

    return docRef.id
  } catch (error) {
    console.error('Error saving design:', error)
    throw error
  }
}

/**
 * Subscribe to user's design history
 */
export const subscribeToDesignHistory = (userId, callback) => {
  const q = query(
    collection(db, `artifacts/${APP_ID}/users/${userId}/ece_designs_fusion`),
    orderBy('createdAt', 'desc')
  )

  return onSnapshot(q, (snapshot) => {
    const designs = snapshot.docs.map((doc) => ({
      id: doc.id,
      ...doc.data(),
    }))
    callback(designs)
  })
}

/**
 * Load a specific design by ID
 */
export const loadDesign = async (userId, designId) => {
  try {
    const docRef = doc(db, `artifacts/${APP_ID}/users/${userId}/ece_designs_fusion`, designId)
    const docSnap = await getDoc(docRef)

    if (docSnap.exists()) {
      return {
        id: docSnap.id,
        ...docSnap.data(),
      }
    } else {
      throw new Error('Design not found')
    }
  } catch (error) {
    console.error('Error loading design:', error)
    throw error
  }
}

