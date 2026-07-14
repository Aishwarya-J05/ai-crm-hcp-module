import { configureStore } from "@reduxjs/toolkit";

import interactionsReducer from "../features/interactions/interactionsSlice.js";

export const store = configureStore({
  reducer: {
    interactions: interactionsReducer,
  },
});
