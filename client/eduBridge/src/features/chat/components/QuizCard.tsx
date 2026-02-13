import React, { useState } from 'react';
import {
  Paper,
  Typography,
  Box,
  RadioGroup,
  Radio,
  FormControlLabel,
  Button,
  Divider,
} from '@mui/material';

export interface QuizQuestion {
  id: string;
  question: string;
  options: string[];
  correctAnswer?: string; // hidden from user
}

export interface QuizData {
  id: string;
  title: string;
  questions: QuizQuestion[];
  documentSource: string[];
}

interface QuizCardProps {
  quiz: QuizData;
  onSubmit?: (answers: Record<string, string>) => void;
}

const QuizCard: React.FC<QuizCardProps> = ({ quiz, onSubmit }) => {
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [submitted, setSubmitted] = useState(false);

  const handleAnswerChange = (questionId: string, value: string) => {
    setAnswers({ ...answers, [questionId]: value });
  };

  const handleSubmit = () => {
    onSubmit?.(answers);
    setSubmitted(true);
  };

  return (
    <Paper
      elevation={3}
      sx={{
        p: 2,
        maxWidth: 500,
        backgroundColor: (theme) =>
          theme.palette.mode === 'light' ? 'grey.50' : 'grey.900',
        borderRadius: 2,
      }}
    >
      <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
        {quiz.title}
      </Typography>
      <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 1 }}>
        Based on: {quiz.documentSource.join(', ')}
      </Typography>
      <Divider sx={{ my: 1.5 }} />
      
      {quiz.questions.map((q, idx) => (
        <Box key={q.id} sx={{ mb: 2 }}>
          <Typography variant="body2" fontWeight="medium" gutterBottom>
            {idx + 1}. {q.question}
          </Typography>
          <RadioGroup
            name={`question-${q.id}`}
            value={answers[q.id] || ''}
            onChange={(e) => handleAnswerChange(q.id, e.target.value)}
          >
            {q.options.map((option, optIdx) => (
              <FormControlLabel
                key={optIdx}
                value={option}
                control={<Radio size="small" />}
                label={option}
                disabled={submitted}
              />
            ))}
          </RadioGroup>
        </Box>
      ))}
      
      {!submitted ? (
        <Button
          variant="contained"
          size="small"
          onClick={handleSubmit}
          disabled={Object.keys(answers).length !== quiz.questions.length}
          sx={{ mt: 1 }}
        >
          Submit Answers
        </Button>
      ) : (
        <Typography variant="body2" color="success.main" sx={{ mt: 1 }}>
          Answers submitted! (Demo)
        </Typography>
      )}
    </Paper>
  );
};

export default QuizCard;