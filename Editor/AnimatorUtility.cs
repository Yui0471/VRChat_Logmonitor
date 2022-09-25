using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using UnityEngine;
using UnityEditor;
using UnityEditor.Animations;


class AnimatorUtility {
    public static AnimatorControllerLayer CloneLayer(AnimatorControllerLayer orig, AnimatorController destController) {
        //Get Asset Path
        string assetPath = AssetDatabase.GetAssetPath(destController);
        AnimatorControllerLayer dest = new AnimatorControllerLayer();
        dest.name = orig.name;
        dest.defaultWeight = orig.defaultWeight;
        dest.avatarMask = orig.avatarMask;
        dest.iKPass = orig.iKPass;
        dest.syncedLayerAffectsTiming = orig.syncedLayerAffectsTiming;
        dest.syncedLayerIndex = orig.syncedLayerIndex;
        dest.blendingMode = orig.blendingMode;

        if(orig.stateMachine != null) {
            dest.stateMachine = CloneStateMachine(orig.stateMachine, assetPath);
            //StateMachineをControllerに保存
            AssetDatabase.AddObjectToAsset(dest.stateMachine, assetPath);
        }
        if(destController != null) {
            destController.AddLayer(dest);
        }
        return dest;
    }

    public static AnimatorStateMachine CloneStateMachine(AnimatorStateMachine orig, string assetPath) {
        AnimatorStateMachine dest = new AnimatorStateMachine();
        List<ChildAnimatorState> destStatesList = new List<ChildAnimatorState>();
        //StateをClone
        foreach(var child in orig.states) {
            AnimatorState state = CloneState(child.state, assetPath);
            destStatesList.Add(new ChildAnimatorState {
                state = state,
                position = child.position
            });
            if(assetPath != "") {
                //StateをControllerに保存
                AssetDatabase.AddObjectToAsset(state, assetPath);
            }
        }
        dest.states = destStatesList.ToArray();

        dest.anyStatePosition = orig.anyStatePosition;
        

        List<StateMachineBehaviour> destBehaviours = new List<StateMachineBehaviour>();
        foreach (var behaviour in orig.behaviours) {
            StateMachineBehaviour destBehaviour = UnityEngine.Object.Instantiate(behaviour);
            destBehaviours.Add(destBehaviour);  
            destBehaviour.name = "";
            //Instantiateでコピーされないし、HideInHierarchyにしないと、nameが同じになって親がすり替えられる？？？
            destBehaviour.hideFlags = HideFlags.HideInHierarchy;
            AssetDatabase.AddObjectToAsset(destBehaviour, assetPath);
        }
        dest.behaviours = destBehaviours.ToArray();
        dest.entryPosition = orig.entryPosition;
        dest.exitPosition = orig.exitPosition;
        dest.name = orig.name;
        dest.hideFlags = orig.hideFlags;

        //Transitionを作成
        MakeTransition(orig, dest, assetPath);
        return dest;
    }

    public static AnimatorState CloneState(AnimatorState orig, string assetPath) {
        AnimatorState dest = new AnimatorState();
        //state本体をClone
        //behaviours
        List<StateMachineBehaviour> destBehaviours = new List<StateMachineBehaviour>();
        foreach(var behaviour in orig.behaviours) {
            StateMachineBehaviour destBehaviour = UnityEngine.Object.Instantiate(behaviour);
            destBehaviours.Add(destBehaviour);
            destBehaviour.name = "";
            //Instantiateでコピーされないし、HideInHierarchyにしないと、nameが同じになって親がすり替えられる？？？
            destBehaviour.hideFlags = HideFlags.HideInHierarchy;
            AssetDatabase.AddObjectToAsset(destBehaviour, assetPath);
        }
        dest.behaviours = destBehaviours.ToArray();

        dest.cycleOffset = orig.cycleOffset;
        dest.cycleOffsetParameter = orig.cycleOffsetParameter;
        dest.cycleOffsetParameterActive = orig.cycleOffsetParameterActive;
        dest.iKOnFeet = orig.iKOnFeet;
        dest.mirror = orig.mirror;
        dest.mirrorParameter = orig.mirrorParameter;
        dest.mirrorParameterActive = orig.mirrorParameterActive;
        dest.motion = orig.motion;
        dest.speed = orig.speed;
        dest.speedParameter = orig.speedParameter;
        dest.speedParameterActive = orig.speedParameterActive;
        dest.writeDefaultValues = orig.writeDefaultValues;
        dest.name = orig.name;
        dest.hideFlags = orig.hideFlags;

        //Transition
        foreach (var transition in orig.transitions) {
            AnimatorStateTransition destTransition;
            if(transition.destinationState == null) {
                //exit
                destTransition = dest.AddExitTransition();
            } else {
                //一旦オリジナルのインスタンスを入れておく
                destTransition = dest.AddTransition(transition.destinationState);
            }
            //Parameter
            destTransition.canTransitionToSelf = transition.canTransitionToSelf;
            destTransition.duration = transition.duration;
            destTransition.exitTime = transition.exitTime;
            destTransition.hasExitTime = transition.hasExitTime;
            destTransition.hasFixedDuration = transition.hasFixedDuration;
            destTransition.interruptionSource = transition.interruptionSource;
            destTransition.offset = transition.offset;
            destTransition.orderedInterruption = transition.orderedInterruption;
            //AnimatorTransitionBase
            destTransition.isExit = transition.isExit;
            destTransition.mute = transition.mute;
            destTransition.solo = transition.solo;
            destTransition.hideFlags = transition.hideFlags;
            destTransition.name = transition.name;
            destTransition.conditions = (AnimatorCondition[])transition.conditions.Clone();

            if(assetPath != "") {
                //Transitionを保存
                AssetDatabase.AddObjectToAsset(destTransition, assetPath);
            }
        }
        return dest;
    }


    private static void MakeTransition(AnimatorStateMachine orig, AnimatorStateMachine dest, string assetPath) {
        //Entry
        ChildAnimatorState[] origChild = orig.states;
        ChildAnimatorState[] destChild = dest.states;
        foreach (var transition in orig.entryTransitions) {
            //TransitionのDestinationを取得
            AnimatorState state = origChild
                                    .Select((child, index) => new { child, index})
                                    .Where(obj => obj.child.state == transition.destinationState)
                                    .Select((obj) => destChild[obj.index].state).First();
            //TransitionをClone
            AnimatorTransition destTransition = dest.AddEntryTransition(state);
            destTransition.isExit = transition.isExit;
            destTransition.mute = transition.mute;
            destTransition.solo = transition.solo;
            destTransition.hideFlags = transition.hideFlags;
            destTransition.name = transition.name;
            //conditions
            destTransition.conditions = (AnimatorCondition[])transition.conditions.Clone();

            if (assetPath != "") {
                //Transitionを保存
                AssetDatabase.AddObjectToAsset(destTransition, assetPath);
            }


        }

        //オリジナルのものを置き換え
        foreach(var state in destChild) {
            foreach(var transition in state.state.transitions) {
                //行き先がないものは無視
                if(transition.destinationState == null) {
                    continue;
                }
                AnimatorState clonedState = origChild
                                    .Select((child, index) => new { child, index })
                                    .Where(obj => obj.child.state == transition.destinationState)
                                    .Select((obj) => destChild[obj.index].state).First();
                transition.destinationState = clonedState;
            }
        }

        //defaultState
        dest.defaultState = origChild
                                    .Select((child, index) => new { child, index })
                                    .Where(obj => obj.child.state == orig.defaultState)
                                    .Select((obj) => destChild[obj.index].state).First();

    }

}
