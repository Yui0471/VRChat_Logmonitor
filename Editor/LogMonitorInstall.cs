using System.Linq;
using System.IO;
using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using UnityEngine.Animations;
using UnityEditor.Animations;
using VRC.SDK3.Avatars.Components;
using VRC.SDK3.Avatars.ScriptableObjects;


public enum CheckErrorCode {
    SUCCESS,
    MISSING_ANIMATOR,
    INVALID_AVATAR,
    NOT_HUMANOID,
    MISSING_NECKBONE,
    MISSING_HEADBONE,

}

static class LogMonitorInstall {

    private const string LM_ORIG_PREFAB_GUID = "424f86bcc639c9a4485c3d5e51f85520";
    private const string LM_ORIG_ANIMCONTROLLER_GUID = "29375c58de13596498f99cd1df02e80e";
    private const string LM_ORIG_EXPARAMETER_GUID = "5d1fa4eb6d1f1d042bb511f6e33e28df";
    private const string VRCSDK_EXAMPLE_EXMENU_GUID = "024fb8ef5b3988c46b446863c92f4522";


    public static CheckErrorCode DescriptorCheck(VRCAvatarDescriptor objRoot) {
        Animator animator = objRoot.GetComponent<Animator>();
        if(animator == null) {
            //Animatorが存在しない
            return CheckErrorCode.MISSING_ANIMATOR;
        }
        Avatar avatar = animator.avatar;
        if(avatar == null || !avatar.isValid) {
            //Avatarがセットされていない
            return CheckErrorCode.INVALID_AVATAR;
        }
        
        if(!avatar.isHuman) {
            //Humanoidではない
            return CheckErrorCode.NOT_HUMANOID;
        }

        if(animator.GetBoneTransform(HumanBodyBones.Neck) == null) {
            return CheckErrorCode.MISSING_NECKBONE;
        }

        if(animator.GetBoneTransform(HumanBodyBones.Head) == null) {
            return CheckErrorCode.MISSING_HEADBONE;
        }
        

        return CheckErrorCode.SUCCESS;
    }

    public static bool CheckBroken() {
        if(!File.Exists(AssetDatabase.GUIDToAssetPath(LM_ORIG_PREFAB_GUID))) {
            return false;
        }

        if(!File.Exists(AssetDatabase.GUIDToAssetPath(LM_ORIG_ANIMCONTROLLER_GUID))) {
            return false;
        }

        if(!File.Exists(AssetDatabase.GUIDToAssetPath(LM_ORIG_EXPARAMETER_GUID))) {
            return false;
        }

        return true;
    }

    public static void Install(VRCAvatarDescriptor descriptor, bool backupFlag = true) {

        if(backupFlag) {
            //Prefabを保存
            string backupPath = GenBackupPath("Assets/" + descriptor.gameObject.name + ".prefab");
            PrefabUtility.SaveAsPrefabAsset(descriptor.gameObject, backupPath);
        }

        //Original Prefab取得
        string origPrefabPath = AssetDatabase.GUIDToAssetPath(LM_ORIG_PREFAB_GUID);
        GameObject originalPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(origPrefabPath);

        //Root取得
        string rootPath = Path.GetDirectoryName(origPrefabPath);
        rootPath = rootPath.Replace("\\", "/");


        Vector3 pos = descriptor.ViewPosition;


        //Animator取得
        Animator animator = descriptor.GetComponent<Animator>();


        //Unpack Prefab
        
        GameObject logmonitor = Object.Instantiate(originalPrefab);
        logmonitor.transform.SetParent(descriptor.gameObject.transform);
        logmonitor.name = originalPrefab.name;

        //ViewPositionを加算
        logmonitor.transform.position += pos;

        //Neckボーン取得
        GameObject neckObject = animator.GetBoneTransform(HumanBodyBones.Neck).gameObject;

        //Headボーン取得
        Transform headTransform = animator.GetBoneTransform(HumanBodyBones.Head);

        //Fake Head作成
        GameObject fake = new GameObject("Fake Head");
        GameObjectUtility.SetParentAndAlign(fake, neckObject);
        fake.transform.position = headTransform.position;
        fake.transform.rotation = headTransform.rotation;

        //FakeHeadにParentConstraintを追加
        ParentConstraint constraint = fake.AddComponent<ParentConstraint>();
        constraint.AddSource(new ConstraintSource {
            sourceTransform = headTransform,
            weight = 1.0f
        });

        //ParentConstraintをActiveに
        constraint.constraintActive = true;

        //Parent Constraint Zero
        constraint.translationAtRest = fake.transform.localPosition;
        constraint.rotationAtRest = fake.transform.localRotation.eulerAngles;
        constraint.locked = true;

        //LogMonitorConstraint作成
        GameObject logmonConstraint = new GameObject("Log_Monitor_Constraint");
        logmonConstraint.transform.SetParent(fake.transform);

        logmonConstraint.transform.position = logmonitor.transform.position;
        logmonConstraint.transform.rotation = logmonitor.transform.rotation;
        logmonConstraint.transform.localScale = logmonitor.transform.localScale;

        //Log Monitor - ParentConstraint設定
        constraint = logmonitor.GetComponent<ParentConstraint>();
        constraint.AddSource(new ConstraintSource {
            sourceTransform = logmonConstraint.transform,
            weight = 1.0f
        });

        //Parent Constraint Zero
        constraint.translationAtRest = logmonitor.transform.localPosition;
        constraint.rotationAtRest = logmonitor.transform.localRotation.eulerAngles;

        //ParentConstraintをActiveに
        constraint.constraintActive = true;
        constraint.locked = true;


        //FX　AnimatorController取得
        VRCAvatarDescriptor.CustomAnimLayer fxAnimLayer = (from layer in descriptor.baseAnimationLayers
                                                           where layer.type == VRCAvatarDescriptor.AnimLayerType.FX
                                                           select layer).FirstOrDefault();
        AnimatorController avatarController = fxAnimLayer.animatorController as AnimatorController;

        AnimatorController origAnimController = AssetDatabase.LoadAssetAtPath<AnimatorController>(AssetDatabase.GUIDToAssetPath(LM_ORIG_ANIMCONTROLLER_GUID));

        if (fxAnimLayer.isDefault || avatarController == null) {
            AssetDatabase.CopyAsset(AssetDatabase.GetAssetPath(origAnimController), rootPath + "/Animator_LogMonitor_FXLayer.controller");
            avatarController = AssetDatabase.LoadAssetAtPath<AnimatorController>(rootPath + "/Animator_LogMonitor_FXLayer.controller");
            int controllerindex = descriptor.baseAnimationLayers
                .Select((layer, index) => new { layer = layer, index = index })
                .Where(obj => obj.layer.type == VRCAvatarDescriptor.AnimLayerType.FX)
                .Select(obj => obj.index).First();
            descriptor.baseAnimationLayers[controllerindex].animatorController = avatarController;
            descriptor.baseAnimationLayers[controllerindex].isDefault = false;
                                            

        } else {
            if (backupFlag) {
                //バックアップ
                BackupFile(avatarController);
            }



            //FxLayerにParameterを作成
            avatarController.AddParameter("Log_Monitor", AnimatorControllerParameterType.Int);
            avatarController.AddParameter("Log_Monitor_ON", AnimatorControllerParameterType.Bool);

            //LayerをAvaterのFXLayerに作成
            AnimatorUtility.CloneLayer(origAnimController.layers[1], avatarController);
            AnimatorUtility.CloneLayer(origAnimController.layers[2], avatarController);

            AssetDatabase.SaveAssets();
            EditorUtility.SetDirty(avatarController);
        }

        //EXParameterに追加
        //未セット、デフォルト、設定済みで分岐
        VRCExpressionParameters exParameters = descriptor.expressionParameters;
        VRCExpressionParameters origParameters = AssetDatabase.LoadAssetAtPath<VRCExpressionParameters>(AssetDatabase.GUIDToAssetPath(LM_ORIG_EXPARAMETER_GUID));
        VRCExpressionParameters expressionParameters = exParameters;
        string exParamPath = AssetDatabase.GetAssetPath(exParameters);
        if (exParameters == null) {
            //未セット
            //アセットをそのままセット
            AssetDatabase.CreateAsset(ScriptableObject.CreateInstance<VRCExpressionParameters>(), rootPath + "/LogMonitor_Expression_Parameters.asset");
            expressionParameters = AssetDatabase.LoadAssetAtPath<VRCExpressionParameters>(rootPath + "/LogMonitor_Expression_Parameters.asset");
            descriptor.expressionParameters = expressionParameters;
            if (!descriptor.customExpressions) {
                string path = GetVRCSDKExmenuPath();
                if(path == "") {
                    AssetDatabase.CreateAsset(ScriptableObject.CreateInstance<VRCExpressionsMenu>(), rootPath + "/Empty_Expression_Menu.asset");
                    path = rootPath + "/Empty_Expression_Menu.asset";
                }
                //CustomExpressionじゃない場合はnullの可能性があるのでサンプルを入れる
                descriptor.expressionsMenu = AssetDatabase.LoadAssetAtPath<VRCExpressionsMenu>(path);
                descriptor.customExpressions = true;
            }

        } else if (exParamPath.StartsWith("Packages/com.vrchat.avatars") ||
                    exParamPath.Contains("VRCSDK")) {
            //SDK Sample
            AssetDatabase.CreateAsset(ScriptableObject.CreateInstance<VRCExpressionParameters>(), rootPath + "/LogMonitor_Expression_Parameters.asset");
            expressionParameters = AssetDatabase.LoadAssetAtPath<VRCExpressionParameters>(rootPath + "/LogMonitor_Expression_Parameters.asset");
            descriptor.expressionParameters = expressionParameters;

        } else if(backupFlag) {
            //バックアップ
            BackupFile(exParameters);
        }

        List<VRCExpressionParameters.Parameter> expressionParametersList;
        if (expressionParameters.parameters == null) {
            expressionParametersList = new List<VRCExpressionParameters.Parameter>();
        } else {
            expressionParametersList = expressionParameters.parameters.ToList();
        }
         
        foreach (var origParam in origParameters.parameters) {
            var exparam = (from param in expressionParametersList
                           where param.name == ""
                           select param).FirstOrDefault();
           if (exparam == null) {
                //存在しない場合追加
                exparam = new VRCExpressionParameters.Parameter();
                expressionParametersList.Add(exparam);
           }
           exparam.name = origParam.name;
           exparam.valueType = origParam.valueType;
           exparam.defaultValue = origParam.defaultValue;
           exparam.saved = origParam.saved;
        }
        expressionParameters.parameters = expressionParametersList.ToArray();
        



        logmonitor.SetActive(false);
    }

    private static string GetVRCSDKExmenuPath() {
        //GUID取得
        string exmenupath = AssetDatabase.GUIDToAssetPath(VRCSDK_EXAMPLE_EXMENU_GUID);
        if (exmenupath != "") {
            return exmenupath;
        }

        //検索
        string filter = "t:" + typeof(VRCExpressionsMenu).Name;
        string[] guidAssets = AssetDatabase.FindAssets(filter);

        foreach(var guid in guidAssets) {
            string path = AssetDatabase.GUIDToAssetPath(guid);
            if(path.StartsWith("Packages/com.vrchat.avatars") || 
                path.Contains("VRCSDK")) {
                return path;
            } 
        }
        return "";
    }

    private static void BackupFile(Object originalObj) {
        //バックアップ
        //パスを取得
        string originalPath = AssetDatabase.GetAssetPath(originalObj);

        string backupPath = GenBackupPath(originalPath);
        //コピー
        AssetDatabase.CopyAsset(originalPath, backupPath);
    }

    private static string GenBackupPath(string originalPath) {
        string dirPath = Path.GetDirectoryName(originalPath);
        string fileName = Path.GetFileNameWithoutExtension(originalPath);
        string fileExt = Path.GetExtension(originalPath);

        //連番を足して存在しないパスを生成
        string backupPath;
        int count = 1;
        do {
            if (count == 1) {
                //1つ目の場合はカウントを付けない
                backupPath = dirPath + "/" + fileName + "_lmback" + fileExt;
            } else {
                backupPath = dirPath + "/" + fileName + "_lmback" + count + fileExt;
            }
            count++;
        } while (File.Exists(backupPath));
        //Path区切りを一応置き換え
        backupPath = backupPath.Replace("\\", "/");
        return backupPath;
    }

    public static int GetRequireParamCost() {
        VRCExpressionParameters origParams =
            AssetDatabase.LoadAssetAtPath<VRCExpressionParameters>(AssetDatabase.GUIDToAssetPath(LM_ORIG_EXPARAMETER_GUID));

        return origParams.CalcTotalCost();

    }

}
