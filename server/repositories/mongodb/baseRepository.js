import mongoose from 'mongoose';

class MongoBaseRepository {
  constructor(collectionName) {
    this.collectionName = collectionName;
  }

  get collection() {
    return mongoose.connection.collection(this.collectionName);
  }

  withoutMongoId(document) {
    if (!document) {
      return null;
    }

    const { _id, ...rest } = document;
    return rest;
  }
}

export default MongoBaseRepository;
