<center>

# ExpoAssistant

An AI assistant to help people get around in a science fair! It also takes feedback!

</center>

ExpoAssistant, or ExpoBot is a collection of python applications which work together to create an AI assistant to help people get around in a science fair.

It is designed to make sure all people can get all the information they need, and to make sure that the science fair is a fun experience for everyone.

It also takes feedback, so that the fair can improve itself and become better the next year. It does this by tagging people's faces with their feedback, and then saving it to a CSV file.

## Features
WIP [readme]


## How it works
WIP [readme]

## How to use
Just open a terminal. Clone this repo, and `cd` into it.

Then, install the requirements:

```python -m pip install -r requirements.txt```

### Running the bot
To run the bot, run:

```
python UI/main.py
```
Then, open up another terminal, and run:

```
python bot.py
```

### Running the feedback system
To run the feedback system, run:

```
python Feedback/facerec.py
```

Then, open up another terminal, and run:

```
python Feedback/main.py
```

## How to contribute
If you want to contribute, just fork this repo, and make a pull request. We will review it, and if it is good, we will merge it.

## Roadmap
- [x] Basic bot functionality
- [x] Basic feedback system
- [x] Feedback system with face recognition
- [x] Basic UI
- [x] Offline text-to-speech
- [ ] GPT Integration

## Credits
- A Teacher Of Mine (Anonymous) - Idea, Team mentor
- [N3RDIUM](https://n3rdium.dev) - Project lead, developer
- Kaede - Graphics
- _____ - GPT Integration [IN PROGRESS]