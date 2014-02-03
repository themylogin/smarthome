char pcState[9] = "";

void setup()
{
  for (int i = 10; i <= 12; i++)
  {
    pinMode(i, INPUT_PULLUP);
  }
  for (int i = A0; i <= A4; i++)
  {
    pinMode(i, INPUT);
    digitalWrite(i, HIGH);
  }
  
  for (int i = 2; i <= 9; i++)
  {
    pinMode(i, OUTPUT);
  }
  
  Serial.begin(9600);
}

void loop()
{
  if (Serial.available() > 1)
  {
    char command = Serial.read();
    if (command == '?')
    {
      Serial.read();
      Serial.println(pcState);
    }
    if (command == 't')
    {
      int port = Serial.read() - '0';      
      Serial.read();
      port = port + 1;
      if (port >= 2 && port <= 9)
      {
        digitalWrite(port, HIGH);
        delay(100);
        digitalWrite(port, LOW);
      }
    }
  }
  
  char state[9];
  getState(state);
  if (strcmp(state, pcState))
  {
    delay(50);
    getState(state);
    Serial.println(state);
    strcpy(pcState, state);
  }
}

void getState(char state[9])
{  
  for (int port = 10, i = 0; port <= 12; port++, i++)
  {
    if (digitalRead(port))
    {
      state[i] = '0';
    }
    else
    {
      state[i] = '1';
    }
  }
  for (int port = A0, i = 3; port <= A4; port++, i++)
  {
    if (analogRead(port) < 512)
    {
      state[i] = '1';
    }
    else
    {
      state[i] = '0';
    }
  }
  
  state[8] = '\0';
}

