import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";

import { api } from "../../services/api.js";

const now = new Date();
const today = now.toISOString().slice(0, 10);
const currentTime = now.toTimeString().slice(0, 5);

const initialForm = {
  hcp_name: "",
  interaction_type: "Meeting",
  interaction_date: today,
  interaction_time: currentTime,
  attendees: "",
  topics_discussed: "",
  materials_shared: "",
  samples_distributed: "",
  sentiment: "Neutral",
  outcomes: "",
  follow_up_actions: "",
  ai_summary: "",
};

export const fetchInteractions = createAsyncThunk("interactions/fetch", api.listInteractions);
export const submitInteraction = createAsyncThunk("interactions/submit", api.createInteraction);
export const sendChatMessage = createAsyncThunk("interactions/chat", api.chat);

const interactionsSlice = createSlice({
  name: "interactions",
  initialState: {
    form: initialForm,
    items: [],
    chat: [
      {
        role: "assistant",
        text: 'Log interaction details here, e.g. "Met Dr. Smith, discussed Product X efficacy, positive sentiment, shared brochure" or ask for follow-up help.',
      },
    ],
    status: "idle",
    error: null,
    lastTool: null,
  },
  reducers: {
    updateField(state, action) {
      const { name, value } = action.payload;
      state.form[name] = value;
    },
    applySuggestion(state, action) {
      state.form.follow_up_actions = action.payload;
    },
    resetForm(state) {
      state.form = { ...initialForm };
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchInteractions.fulfilled, (state, action) => {
        state.items = action.payload;
      })
      .addCase(submitInteraction.pending, (state) => {
        state.status = "saving";
        state.error = null;
      })
      .addCase(submitInteraction.fulfilled, (state, action) => {
        state.status = "idle";
        state.items.unshift(action.payload);
        state.form = { ...initialForm };
        state.chat.push({ role: "assistant", text: `Saved interaction for ${action.payload.hcp_name}.` });
      })
      .addCase(submitInteraction.rejected, (state, action) => {
        state.status = "error";
        state.error = action.error.message;
      })
      .addCase(sendChatMessage.pending, (state, action) => {
        state.status = "thinking";
        state.error = null;
        state.chat.push({ role: "user", text: action.meta.arg });
      })
      .addCase(sendChatMessage.fulfilled, (state, action) => {
        state.status = "idle";
        state.lastTool = action.payload.tool;
        if (
          ["log_interaction", "edit_interaction"].includes(action.payload.tool)
          && action.payload.data?.id
        ) {
          state.items = [
            action.payload.data,
            ...state.items.filter((item) => item.id !== action.payload.data.id),
          ];
          state.form = {
            ...state.form,
            ...action.payload.data,
            interaction_time: action.payload.data.interaction_time?.slice(0, 5) || state.form.interaction_time,
          };
        }
        state.chat.push({
          role: "assistant",
          text: `${action.payload.message} Tool: ${action.payload.tool}.`,
          data: action.payload.data,
        });
      })
      .addCase(sendChatMessage.rejected, (state, action) => {
        state.status = "error";
        state.error = action.error.message;
        state.chat.push({ role: "assistant", text: "I could not reach the backend agent." });
      });
  },
});

export const { applySuggestion, resetForm, updateField } = interactionsSlice.actions;
export default interactionsSlice.reducer;
