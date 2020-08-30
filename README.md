# Closkell
Closkell is a dependantly and dynamically typed, purely functional programming language with goodies from both Haskell and Clojure. The language is currently in its alpha release therefore the only way to interact with it right now is the use of the repl.

# Defining a variable
## Let Binding
Saying variabe may be a reach since you can't really change its value because it's immutable, a better term would be defining a constant or perhaps defining a function. Since, the first binding we'll see is a recursive function based binding. It's known as `let` binding and here's how you perform it,
```
let x = 5
```
Now `x` has become a nullary function so whenever it's called, it would result in the same value that in this case being 5.

## Val binding
Sometimes you don't really want your bindings to be recursive and for those times we have `val` bindings, they never define a function and are strictly evaluated. They can be use by saying,
```
val x = 5
```
The important difference to notice here is that `x` was evaluated while it was being defined, not when it was called.

# Function definition
## Let Construct
Being a functional language, the most important construt in Closkell is function definition but there is no single way to define a function, it largely depends on how and what you want your function to be. The first definition construct we would discuss is the simplest one, the `let` construct. It's very similar to the variable defintion and here's how you do it.
```
let add a b = a+b
```
Here `add` is a function that takes two arguments namely, `a` and `b` and returns their sum.

## Lambda functions
You **cannot** simple say
```
val add a b = a+b
```
since `val` never defines specififcally defines a function, it rather defines a value. So in order to make the above work, you use lambda functions like this.
```
val add = \a b -> a+b
```
And it would be semtantically equivilant to the aforementioned function defined by the `let` construct.

## Curry definition
Currying in Closkell can be done in multiple ways and the most painful, yet simplest way of defining curried functions is to either say
```
let add = \a -> \b -> a+b
```
or
```
val add = \ -> \a -> \b -> a+b
```
but the idiomatic way of defining curried functions in Closkell is to actually use the `curry` curry and let it do the dirty work for you. Here's an example of how you would use it,
```
curry add a b = a+b
```
See how it's way more clean and clutter-free while being a semantic equivilant of the other two.

# Calling a function
## Simple Function call
After defining a function, it's of no use if you do not call it and there are, as there were with definitions, multiple ways to call a function depending on the purpose of the call. The first call we'll cover is the simplest and the one you'd be using most of the time. Here's what it looks like, to call the non-curried `add` function that was defined earlier.
```
add 2 2
```
and it results in 4

## Expression call
An expression call is basically a function call but instead of function you are calling a specific expression this time around and it works like this,
```
!(\a b -> a+b) 2 2
```
Here the lambda function that adds two integers is being defined and called in the same line via lambda functions.

## Not Calling a function
What you would recogonize is that whenever you want do something to a function without calling it, you'd need the help of `!` again. It works like this,
```
add!
```
And we can pass it around without evaluating it right away because saying `add` would be same as calling `add` with no arguments.

## Calling curried functions
The obvious and obviously painful way of calling curried functions in Closkell is,
```
!(!(add) 2) 2
```
but I hear you scream "that's atrocious for a functional language" and that's why there are curried calls, like this.
```
add: 1, 2
```
Now, that definetly sounds more humane and is the idiomatic way of doing it so this is what you should do when calling a curried function.

## Infix calls
As usual for ML-Like languages there's a custom infix operator that has the sole purpose of being a more convinient function call. It works like this,
```
2 `add` 2
```
and that quite obviously returns 4.

## Pipeline operator
There's another way of calling a function, by using the pipeline operator to make your life eaiser, like this.
```
inc n = n+1
add(2, 2) |> inc!
```
You can also use the pipeline operator to supply mutiple arguments like this,
```
^[1, 2] |> add! |> inc!
```
# Type System
Even though, Closkell is a dynamically typed language, it still respects types as much as the next language and therefore includes a type system that will help you in using dynamic dispatch and other cool stuff. So let's begin with a type defintion using our good ole' friend `val`.
## Type definition
Type definitions are done by using a `val` and defining a struct, like this.
```
val person = Person{fn, sn}
```
Now, beware that this will define two things, a type representative and a value constructor. The value constructor is the part that's next to the `val` meaning the lowercase `person` and you can call it like a normal function to create it's instance,
```
val john = person "John" "Williams"
```
and this returns a value that's an instance of the CamelCase `Person` and you can verify this, in two ways either by saying
```
john::Person
```
and watching the result to become `true` while the other way is to say
```
::john
```
and let it output `Person` by itself. Now you might be thinking what if I need a constructor then would I need to create another function and the answer is maybe, because there is a default way to modify incoming parameters like this,
```
val person = Person{fn, sn} when val fn, sn = fn+" haha", sn+" No"
```
## Inheritance
Inheritance is a virtually universal concept, but in different ways, here a struct can inherit from another struct by saying something along the lines of,
```
val body = Body{height, weight}
val person = Person{fn, sn} inherits body!
```
and now when you call `Person`'s value constructor we'd have to supply two four arguments, the first two for `height` and `weight`, and the second pair for `fn` and `sn` like this.
```
person 6 75 "John" "Smith"
```
and it would result in
```
Person {height: 6, weight: 75, fn: John, sn: Smith}
```
and now when checking it's type to be either
```
john::Body
```
or
```
john::Person
```
would be true but it actually uses a type stack to setup a hirearchy where the top-most type get's printed out when you say,
```
::john
```
and the top-most type in this case was `Person` since we used the `person` constructor to create this instance. Before you ask, **No constructors are not inherited**.

## Sum Types
The inheritance way of doing sum-types even though quite explicit but just seems varbose for simple records, I mean look at this.
```
val shape = Shape{}.
val circle = Circle{r} inherits shape!.
val square = Square{edge} inherits shape!.
val triangle = Triangle{a, b, c} inherits shape!.
```
Now tell me that this isn't needlessly verbose, and to counter it's verbosity we need some sugar and we have it with the `data` keyword.
```
data shape = Square{edge} || Circle{r} || Triangle{a, b, c}
```
Now, that's some terse code that we can get behind, and the best part is that it's more or less semantically equivilant to the verbose monstrocity that we wrote before it. Ok, I was lying, it's not exactly semantically equivilant since it introduces a master value constructor shape that's quite different from the one introduced by the code we used before this. This one takes an arbitrary amount of parameters and then passes it to every constructor stored inside it and returns `null` if it matches to non and you can even have conditions as to when they should match like this.
```
data shape = Square{edge} -> edge::Number || Circle{r} -> r::Number || Err{}
```
But these conditions will only be tested if the number of arguments match. Now you may be thinking what if I want an error instead of `null` when none of my patterns match, and for that we have the `default` keyword. You should make a default pattern like this,
```
data shape = Square{edge} -> edge::Number || Circle{r} -> r::Number || default Err{}
```
and it would start raising the error `No patterm matched including the default` instead of returning `null`.

## Base DataTypes
Here are the basic data types that the langugae provides, I will only show little functionality of them as you may already be familiar with them from other programming langugaes,
### Numbers
```
2+2
```
### NullType
```
null
```
### Bool
```
true or false
```
### Lists
```
[1, 2, 3] + [4, 5]
```
### Sets
```
#{1, 2, 3} * #{4, 5}
```
### Maps
```
{"a": 5, "b": "Hello"} + {"c": 7, "d": "Hey"}
```
### Strings
```
"The string"
```
### Tuples
```
val a, b, c = (1, 2, 3)
```
That's all. You now know about every base type closkell provides.

# Case Covering
## If expressions
We would start by the simplest context that you can find in any language that allows you to cover different cases and make decisions based on boolean values, and the first expression is `if` expression, and most of youd already know that you use it like this,
```
let classifier n = if n == 5 then "equal" elif n>5 then "big" else "small"
```
## Pattern expressions
Now `if` expression quite famously become redundant after a while and for those cases there are two constructs, the first one being patterns
```
let classifier n = | n == 5 -> "equal" | n>5 -> "big" | "small"
```
## Case exressions
but when we need to see if things are equal and cover cases there, we reach for case expressions
```
let equaler n = case n -> | 5 -> "five" | 6 -> "six" | "weird"
```
Both in pattern and case expressions you can use a `where` clause to define stuff like this,
```
let equaler n = case n -> | x -> "five" | y -> "six" | "weird" where x, y = 5, 6
```
and
```
let classifier n = | n == const -> "equal" | n>const -> "big" | "small" where const = 5
```
### Nature of Types
Types in this language are very much similar to how they are in "mainstream" dependantly typed and total functional languages. Here types are first classes, which entails that they can be treated just like values. All operations on values can also be performed on types, and vice versa. This is why you do not need a generics system since generics are also just very simple variables. Because of types literally being values, you can
```
::john + "s"
```
where `john` is a `Person` type and here the resulting type would be `Persons` type which was just created for us by mangling a few types together.
## PolyMorphism with case classes
PolyMorphism is very important when it comes to programming, especially in both OO an functional langugaes since their entire base is set on a sngle component. Closkell supports polymorphism through multimethods which are expressed here, in terms of case/classes. Like this,
```
class fac n
case fac n==1 -> 1
case fac default -> n*fac n-1
```
and saying `fac 5` here return `120`. Now let's see a somewhat more interesting form of polymorphism that will introduce new bindings, like what follows,
```
data shape = Circle{r} || Square{edge} || Triangle{a, b, c}

class area obj where r, edge, a, b, c = obj => r, obj => edge, obj => a, obj => b, obj => c
case area obj::Circle -> 3.14*r*r
case area obj::Square -> edge*edge
case area obj::Triangle -> (a*b)/c
```
Here you see that `where` clause again, while defining the class introduces new variables, by accessing fields of existing variables with the use of `=>` operator. Now you will very soon realize that it is more or less redundant to access all possible fields so there's an easier way to do that and it is this,
```
data shape = Circle{r} || Square{edge} || Triangle{a, b, c}

class area obj where {} = obj
case area obj::Circle -> 3.14*r*r
case area obj::Square -> edge*edge
case area obj::Triangle -> (a*b)/c
```
Here it makes the instance turns the instance it gets into our environment so we can access all the fields.
### To be continued...
