using UnityEngine;
using UnityEngine.Animations;
using UnityEditor;
using UnityEngine.UIElements;
using UnityEditor.UIElements;
using UnityEditor.Animations;
using VRC.SDK3.Avatars.Components;
using VRC.SDK3.Avatars.ScriptableObjects;
using System.Linq;
using System.Collections.Generic;
using System.IO;

public class LogMonitorUIElement : EditorWindow {
    private const string LAYOUT_UXML_GUID = "37e2f1ca14323f744af4615403374007";
    private const string STYLESHEET_USS_GUID = "28c045968fb2a274f9635f37490406fd";

    private string strErrorHelpBox = "";
    // メニューに追加
    [MenuItem("Yuis Miniature Garden/Log Monitor")]
    public static void ShowWindow() {
        // ウィンドウの作成
        var wnd = GetWindow<LogMonitorUIElement>();
        // ウィンドウタイトルの設定
        wnd.titleContent = new GUIContent("Log Monitor");
    }
    
    private void OnEnable() {
        VisualTreeAsset tree = AssetDatabase.LoadAssetAtPath<VisualTreeAsset>(AssetDatabase.GUIDToAssetPath(LAYOUT_UXML_GUID));

        VisualElement root = tree.CloneTree();

        var styleSheet = AssetDatabase.LoadAssetAtPath<StyleSheet>(AssetDatabase.GUIDToAssetPath(STYLESHEET_USS_GUID));
        root.styleSheets.Add(styleSheet);

        Button button = root.Q<Button>("add_button");
        button.SetEnabled(false);

        IMGUIContainer imguiErrBox = root.Q<IMGUIContainer>("error_helpbox");
        imguiErrBox.onGUIHandler += () => {
            EditorGUILayout.HelpBox(strErrorHelpBox, MessageType.Error);
        };
        imguiErrBox.visible = false;

        ObjectField field = root.Q<ObjectField>("vrcdescriptor_objfield");
        field.objectType = typeof(VRCAvatarDescriptor);
        field.RegisterValueChangedCallback(e => {
            Reset();
        });


        button.clicked += () => {

            VRCAvatarDescriptor descriptor = field.value as VRCAvatarDescriptor;

            LogMonitorInstall.Install(descriptor);

        };


        rootVisualElement.Add(root);

    }

    void SetCostGage(int max, int used, int require) {
        VisualElement root = this.rootVisualElement;
        Box elmUsed = root.Q<Box>("avatar_paramcost_used");
        Box elmRequire = root.Q<Box>("avatar_paramcost_require");
        Label elmUseLabel = root.Q<Label>("avatar_paramcost_labeluse");
        Label elmFreeLabel = root.Q<Label>("avatar_paramcost_labelfree");
        
        elmUsed.style.width = new StyleLength(Length.Percent(used / (max * 1.0f) * 100.0f));
        elmRequire.style.width = new StyleLength(Length.Percent(require / (max * 1.0f) * 100));

        if (max == 0) {
            elmUseLabel.text = " ";
            elmFreeLabel.text = " ";
        } else {
            elmUseLabel.text = $"{used} + {require} ({used+require}) / {max}";
            elmFreeLabel.text = $"空き: {max - used} - {require} ({max - used - require})";
        }
    }

    int CalcExParamCost(VRCExpressionParameters exparams) {
        if(exparams == null) {
            return 0;
        }

        var validParamsType = from param in exparams.parameters
                          where param.name != ""
                          select param.valueType;

        int total = 0;
        foreach(var paramType in validParamsType) {
            total += VRCExpressionParameters.TypeCost(paramType);
        }
        return total;
    }

    private void OnFocus() {
        //Debug.Log("OnFocus()");

        IMGUIContainer imguiErrBox = this.rootVisualElement.Q<IMGUIContainer>("error_helpbox");
        ObjectField field = this.rootVisualElement.Q<ObjectField>("vrcdescriptor_objfield");

        //ファイルチェック
        if (!LogMonitorInstall.CheckBroken()) {
            Debug.Log("test");
            strErrorHelpBox = "パッケージが破損しています。UnityPackageを再インポートしてください。";
            
            imguiErrBox.visible = true;
            imguiErrBox.MarkDirtyRepaint();
            field.SetEnabled(false);
            return;
        } else {
            strErrorHelpBox = "";
            imguiErrBox.visible = false;
            imguiErrBox.MarkDirtyRepaint();
            field.SetEnabled(true);
        }
        Reset();
        
    }

    public void Reset() {
        VisualElement root = this.rootVisualElement;
        Button button = root.Q<Button>("add_button");
        if(button == null) {
            return;
        }
        button.SetEnabled(false);

        IMGUIContainer imguiErrBox = root.Q<IMGUIContainer>("error_helpbox");

        ObjectField field = root.Q<ObjectField>("vrcdescriptor_objfield");
        field.objectType = typeof(VRCAvatarDescriptor);

        if (field.value != null && field.value is VRCAvatarDescriptor) {
            VRCAvatarDescriptor descriptor = (VRCAvatarDescriptor)field.value;

            int used = CalcExParamCost(descriptor.expressionParameters);

            SetCostGage(VRCExpressionParameters.MAX_PARAMETER_COST, used, LogMonitorInstall.GetRequireParamCost());


            CheckErrorCode err = LogMonitorInstall.DescriptorCheck(descriptor);

            switch (err) {
                case CheckErrorCode.MISSING_ANIMATOR:
                    strErrorHelpBox =
                        $"\"{descriptor.gameObject.name}\"にはAnimator Componentが存在しません";
                    break;

                case CheckErrorCode.INVALID_AVATAR:
                    strErrorHelpBox =
                        $"\"{descriptor.gameObject.name}\"のAnimatorにAvatarがセットされていないか、\n" +
                        "無効なAvatarです";
                    break;

                case CheckErrorCode.NOT_HUMANOID:
                    strErrorHelpBox =
                        $"\"{descriptor.gameObject.name}\"のAvatarはHumanoidではありません。\n" +
                        $"Humanoidである必要があります。";
                    break;

                case CheckErrorCode.MISSING_NECKBONE:
                    strErrorHelpBox =
                        $"\"{descriptor.gameObject.name}\"にはNeckボーンが存在しないか、Mappingにセットされていません。\n" +
                        $"Neck、Headボーンが必要です。";
                    break;

                case CheckErrorCode.MISSING_HEADBONE:
                    strErrorHelpBox =
                        $"\"{descriptor.gameObject.name}\"にはHeadボーンが存在しないか、Mappingにセットされていません。\n" +
                        $"Neck、Headボーンが必要です。";
                    break;

            }

            if (err != CheckErrorCode.SUCCESS) {
                imguiErrBox.visible = true;
                button.SetEnabled(false);
            } else {
                imguiErrBox.visible = false;
                strErrorHelpBox = "";
                button.SetEnabled(true);
            }
        } else {
            imguiErrBox.visible = false;
            SetCostGage(0, 0, 0);
            button.SetEnabled(false);
        }
    }

}