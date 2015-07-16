Ranking items using a Bradley-Terry model.


Paper Citation:
http://projecteuclid.org/euclid.aos/1079120141


Here is the model we're working with:
    P(X beats Y) = strength(x) / (strength(x) + strength(y))

where P(x beats y) is the probability that "x beats y"; x has a higer rank
than y does. You can write this as

    P(x > y) = etc.

I think it's pretty intuitive notation. I'll use it because it's less
keystrokes and I'm lazy.

Then:
    strength(x)
is a function that outputs a number*. This number is measuring whatever
quality you're ranking for the item x.

Intuitively, the higher the value of strength(x), the more of the quality
you're measuring x has. (The better it's rank, in theory.)

For example:
    Say I'm trying to rank my top 10 favorite baked sweets.
        Cake is #3
        Pie is #5
        (brownies are at least #2. #1 is corner-of-the-pan brownies)

        If strength values are a number between 1 and 10 (inclusive),
            strength(corner-brownies) = 10
            ...
            strength(cake) = 8
            ...
            strength(pie) = 6
            ... etc.

    Remember our model, P(x > y) = strength(x) / (strength(x) + strength(y))

    So, the probability that cake beats pie = about 0.57 **, whereas
    the probability that pie beats cake = only about 0.43.

    We conclude that higher ranked things will be expected to beat lower
    ranked things in a contest. Radical
    
    
So we need a way to store strength values, which is the code object StrengthVector.
Similarly, GameData stores ranked pairs of items.

How do we get accurate strength values for each item? The class Model ties StrengthVector and GameData
together and using a formula in Model.update_strengths, iterates over the data and updates our
strength values, which gives an updated and improved ranking of items.

I also wrote a quick-and-dirty class called Interface which gives an example of how to write code that
can interact with the model and add information to it in a (hopefully) intuitive way.
    

\* There are tricky properties this number needs to have which I can't say I
fully understand, but I think I've dealt with this appropriately in the code.

** That number is a total accident. Life is funny.

P.S.
In the code I throw around the word "game" a lot, I don't think I really
explain what I mean. A game is just a single round between two things
you're comparing.

Also, note that this model cannot handle ties. There is a way to do it but
I can't quite get my head around it. For now, the model essentially ignores
ties.
