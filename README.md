# Rambo-cli
#### A small and simple library to get your cli entry points up and running quickly. 

## Getting Started
 
### Installation
```commandline
pip install rambo-cli
```

### Create a Project
```commandline
rambo new project spam 
```

a few directories and files will be created
```
root
    spam
        entrypoints
            __init__.py
            spam.yml
```

### Creating Your First Entrypoint

Create a file in the `spam/entrypoints` directory

```commandline
touch spam/entrypoints/beans.py
```

````python
# beans.py

from rambo import EntryPoint

class PlaceOrder(EntryPoint):

    def run(self):
        print("I'll have the spam and eggs!")
````

In `spam.yml` add the verb and noun which describes your entry point

```yaml
terminal:
    nouns:
      - order

    verbs:
      - place
```

Now run your command
```commandline
python spam place order
```

If everything worked correctly, on the terminal you should see
```commandline
I'll have the spam and eggs!
```


