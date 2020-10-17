# Rambo-cli
#### A small and simple library to get your cli entry points up and running quickly. 

## Getting Started
 
### Installation
```commandline
pip install rambo-cli
```

### project structure
rambo will look for a directory in your project called `entrypoints` with the below structure where 
`beans.py` and `eggs.py` are files which contain the entrypoints for your cli.

```yaml
app
    entrypoints
      __init__.py
      beans.py
      eggs.py
    other_dirs
   __init__.py
   __main__.py
```

### Creating Your First Entrypoint

Create a file in the `spam/entrypoints` directory


````python
# /entrypoints/beans.py

from rambo import EntryPoint

class Order(EntryPoint):

    def action(self):
        print("I'll have the spam and eggs!")
````

````python
# /entrypoints/beans.py

from rambo import EntryPoint

class Order(EntryPoint):

    def action(self):
        print("I'll have the spam and eggs!")
````

Now run your command
```commandline
python app order
```

If everything worked correctly, on the terminal you should see
```commandline
I'll have the spam and eggs!
```


