
## RoganBot: Adjudicator Module

RoganBot is a bot for the 1v1 versions of the game Diplomacy currently under development. The current repository contains the adjudicator module of RoganBot, and any associated files. The adjudicator may be used as a stand alone module, to run a game of Diplomacy on you local device.

See the Jupyter notebooks in the folder 'examples/' for hands on instructions on how to use the adjudicator as a stand alone module.

For user not familiar with Jupyter notebooks, we recommend that you first install an Individual Edition of Anaconda. 

# A few words on the algorithm

Interesting notes on adjudicator algorithms in general can be found in the article by Kruijswijk:
http://uk.diplom.org/pouch/Zine/S2009M/Kruijswijk/DipMath_Chp1.htm.
The current adjudicator does not, however, follow Kruijswijk's design.

The adjudication is treated as a dynamic process where partial information of orders are updated depending on (partial) information of other orders. An order is marked as resolved if all partial information has been determined. By general properties of the game (see Kruiswijk's notes), if we iteratively loop through all remaining orders then, either, at least order is resolved, or, we have detected a situation with cyclic dependencies. There are two categories of cyclic dependencies: so-called paradoxes and circular movement. The order of resolution is:

 1. Resolve orders, until done or stuck.
 2. If remaining orders, resolve Paradoxes.
 3. Resolve orders until done or stuck.
 4. If remaining orders, resolve Circular movement.
 5. Resolve orders until done.

Paradoxes are resolved by marking all non-resolved moves via convoy as not cutting nor dislodging (i.e., the Szykman rule). Circular movement is resolved by marking all remaining moves as successful. Paradoxes must be resolved before circular movement, because a paradox can have a 'tail' of move orders depending on it, which is not circular and which are not part of the paradox, but whose resolution depends on the resolution of the paradox. A circular movement cannot have such a tail.

The algorithm is currently not optimized. However, it is fast.# RoganBot
