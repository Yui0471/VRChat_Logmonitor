// Unity built-in shader modification. by Yui-Kazeniwa

// Unlit alpha-cutout shader.
// - no lighting
// - no lightmap support
// - no per-material color

Shader "Yuis_Unlit_Transparent_Cutout" {
    Properties {
        _MainTex ("Base (RGB) Trans (A)", 2D) = "white" {}
        _Cutoff ("Alpha cutoff", Range(0,1)) = 0.5
        _CameraRT ("Camera RenderTexture", 2D) = "white" {}
    }

    SubShader {
        Tags {"Queue"="AlphaTest" "IgnoreProjector"="True"
        "RenderType"="TransparentCutout"}
        LOD 100

        Lighting Off

        Pass {
            CGPROGRAM
                #pragma vertex vert
                #pragma fragment frag
                #pragma target 2.0
                #pragma multi_compile_fog

                #include "UnityCG.cginc"

                struct appdata_t {
                    float4 vertex : POSITION;
                    float2 texcoord : TEXCOORD0;
                    UNITY_VERTEX_INPUT_INSTANCE_ID
                };

                struct v2f {
                    float4 vertex : SV_POSITION;
                    float2 texcoord : TEXCOORD0;
                    UNITY_FOG_COORDS(1)
                    UNITY_VERTEX_OUTPUT_STEREO
                };

                sampler2D _MainTex;
                float4 _MainTex_ST;
                fixed _Cutoff;
                float4 _CameraRT_TexelSize;

                bool IsNotInCamera() {
	                return (_ScreenParams.x != _CameraRT_TexelSize.z || 
		                    _ScreenParams.y != _CameraRT_TexelSize.w);
                }

                bool IsNotVRCCameraHD() {
                    return (_ScreenParams.x != 1280 || 
                            _ScreenParams.y != 720);
                }

                bool IsNotVRCCameraFHD() {
                    return (_ScreenParams.x != 1920 || 
                            _ScreenParams.y != 1080);
                }

                bool IsNotVRCCameraQHD() {
                    return (_ScreenParams.x != 2560 || 
                            _ScreenParams.y != 1440);
                }

                bool IsNotVRCCamera4K() {
                    return (_ScreenParams.x != 3840 ||
                            _ScreenParams.y != 2160);
                }

                bool IsNotVRCCamera8K() {
                    return (_ScreenParams.x != 7680 || 
                            _ScreenParams.y != 4320);
                }

                v2f vert (appdata_t v)
                {
                    v2f o;
                    UNITY_SETUP_INSTANCE_ID(v);
                    UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
                    o.vertex = UnityObjectToClipPos(v.vertex);
                    o.texcoord = TRANSFORM_TEX(v.texcoord, _MainTex);
                    o.vertex.xyz *= IsNotInCamera() * 
                                    IsNotVRCCameraHD() * 
                                    IsNotVRCCameraFHD() * 
                                    IsNotVRCCameraQHD() * 
                                    IsNotVRCCamera4K() * 
                                    IsNotVRCCamera8K();
                    UNITY_TRANSFER_FOG(o,o.vertex);
                    return o;
                }

                fixed4 frag (v2f i) : SV_Target
                {
                    if(UNITY_MATRIX_P[2][2] <= 0 ) { clip(-1);}
                    fixed4 col = tex2D(_MainTex, i.texcoord);
                    clip(col.a - _Cutoff);
                    UNITY_APPLY_FOG(i.fogCoord, col);
                    return col;
                }

            ENDCG
        }
    }
}