package com.croger.discipuladorcristaov2;

import android.app.Service;
import android.content.Intent;
import android.graphics.Color;
import android.graphics.PixelFormat;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.os.Build;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import android.provider.Settings;
import android.view.Gravity;
import android.view.MotionEvent;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

import org.json.JSONArray;
import org.json.JSONObject;


public class OverlayService extends Service {

    private WindowManager windowManager;
    private LinearLayout overlayView;
    private WindowManager.LayoutParams params;

    private TextView txtStatus;
    private Button btnAnterior;
    private Button btnProximo;

    private JSONArray fila;
    private int indice = 0;


    @Override
    public void onCreate() {
        super.onCreate();

        windowManager = (WindowManager)
                getSystemService(WINDOW_SERVICE);
    }


    @Override
    public int onStartCommand(
            Intent intent,
            int flags,
            int startId
    ) {

        try {

            if (intent == null) {
                stopSelf();
                return START_NOT_STICKY;
            }

            String dados = intent.getStringExtra(
                    "fila_json"
            );

            if (dados == null || dados.trim().isEmpty()) {
                stopSelf();
                return START_NOT_STICKY;
            }

            fila = new JSONArray(dados);

            if (fila.length() == 0) {
                stopSelf();
                return START_NOT_STICKY;
            }

            indice = 0;

            if (
                Build.VERSION.SDK_INT >= Build.VERSION_CODES.M
                && !Settings.canDrawOverlays(this)
            ) {
                stopSelf();
                return START_NOT_STICKY;
            }

            removerOverlay();

            criarOverlay();

            atualizarStatus();

            new Handler(
                Looper.getMainLooper()
            ).postDelayed(
                new Runnable() {
                    @Override
                    public void run() {
                        abrirWhatsapp(indice);
                    }
                },
                400
            );

        } catch (Exception erro) {

            erro.printStackTrace();
            stopSelf();
        }

        return START_NOT_STICKY;
    }


    private void criarOverlay() {

        overlayView = new LinearLayout(this);

        overlayView.setOrientation(
                LinearLayout.VERTICAL
        );

        overlayView.setPadding(
                24,
                18,
                24,
                18
        );


        GradientDrawable fundo =
                new GradientDrawable();

        fundo.setColor(
                Color.argb(
                        235,
                        25,
                        25,
                        25
                )
        );

        fundo.setCornerRadius(28);

        fundo.setStroke(
                2,
                Color.rgb(
                        210,
                        180,
                        125
                )
        );

        overlayView.setBackground(fundo);


        // ==========================================
        // TÍTULO
        // ==========================================

        TextView titulo =
                new TextView(this);

        titulo.setText(
                "DISCIPULADOR CRISTÃO V2"
        );

        titulo.setTextColor(
                Color.WHITE
        );

        titulo.setTextSize(15);

        titulo.setGravity(
                Gravity.CENTER
        );

        titulo.setPadding(
                10,
                6,
                10,
                10
        );

        overlayView.addView(titulo);


        // ==========================================
        // CONTATO ATUAL
        // ==========================================

        txtStatus =
                new TextView(this);

        txtStatus.setTextColor(
                Color.WHITE
        );

        txtStatus.setTextSize(17);

        txtStatus.setGravity(
                Gravity.CENTER
        );

        txtStatus.setPadding(
                8,
                8,
                8,
                12
        );

        overlayView.addView(
                txtStatus
        );


        // ==========================================
        // ANTERIOR / PRÓXIMO
        // ==========================================

        LinearLayout linha =
                new LinearLayout(this);

        linha.setOrientation(
                LinearLayout.HORIZONTAL
        );

        btnAnterior =
                new Button(this);

        btnAnterior.setText(
                "◀ ANTERIOR"
        );

        btnProximo =
                new Button(this);

        btnProximo.setText(
                "PRÓXIMO ▶"
        );


        LinearLayout.LayoutParams peso =
                new LinearLayout.LayoutParams(
                        0,
                        LinearLayout.LayoutParams.WRAP_CONTENT,
                        1
                );

        linha.addView(
                btnAnterior,
                peso
        );

        linha.addView(
                btnProximo,
                peso
        );

        overlayView.addView(
                linha
        );


        // ==========================================
        // ENCERRAR
        // ==========================================

        Button btnEncerrar =
                new Button(this);

        btnEncerrar.setText(
                "ENCERRAR ENVIO"
        );

        overlayView.addView(
                btnEncerrar
        );


        // ==========================================
        // AÇÕES
        // ==========================================

        btnAnterior.setOnClickListener(
            new View.OnClickListener() {

                @Override
                public void onClick(View v) {

                    if (indice > 0) {

                        indice--;

                        atualizarStatus();

                        abrirWhatsapp(
                                indice
                        );
                    }
                }
            }
        );


        btnProximo.setOnClickListener(
            new View.OnClickListener() {

                @Override
                public void onClick(View v) {

                    if (
                        fila != null
                        && indice < fila.length() - 1
                    ) {

                        indice++;

                        atualizarStatus();

                        abrirWhatsapp(
                                indice
                        );

                    } else {

                        txtStatus.setText(
                                "ÚLTIMO CONTATO DA FILA"
                        );

                        btnProximo.setEnabled(
                                false
                        );
                    }
                }
            }
        );


        btnEncerrar.setOnClickListener(
            new View.OnClickListener() {

                @Override
                public void onClick(View v) {

                    stopSelf();
                }
            }
        );


        // ==========================================
        // JANELA SOBRE OUTROS APPS
        // ==========================================

        int tipo;

        if (
            Build.VERSION.SDK_INT
            >= Build.VERSION_CODES.O
        ) {

            tipo =
                WindowManager.LayoutParams
                .TYPE_APPLICATION_OVERLAY;

        } else {

            tipo =
                WindowManager.LayoutParams
                .TYPE_PHONE;
        }


        params =
            new WindowManager.LayoutParams(
                WindowManager.LayoutParams.WRAP_CONTENT,
                WindowManager.LayoutParams.WRAP_CONTENT,
                tipo,
                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE
                    | WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN,
                PixelFormat.TRANSLUCENT
            );


        params.gravity =
                Gravity.TOP
                | Gravity.END;

        params.x = 20;
        params.y = 180;


        windowManager.addView(
                overlayView,
                params
        );


        // ==========================================
        // ARRASTAR A JANELA PELO TÍTULO
        // ==========================================

        titulo.setOnTouchListener(
            new View.OnTouchListener() {

                private int inicioX;
                private int inicioY;

                private float toqueX;
                private float toqueY;


                @Override
                public boolean onTouch(
                        View v,
                        MotionEvent event
                ) {

                    switch (
                        event.getAction()
                    ) {

                        case MotionEvent.ACTION_DOWN:

                            inicioX =
                                    params.x;

                            inicioY =
                                    params.y;

                            toqueX =
                                    event.getRawX();

                            toqueY =
                                    event.getRawY();

                            return true;


                        case MotionEvent.ACTION_MOVE:

                            params.x =
                                inicioX
                                - (int) (
                                    event.getRawX()
                                    - toqueX
                                );

                            params.y =
                                inicioY
                                + (int) (
                                    event.getRawY()
                                    - toqueY
                                );

                            windowManager.updateViewLayout(
                                    overlayView,
                                    params
                            );

                            return true;
                    }

                    return false;
                }
            }
        );
    }


    private void atualizarStatus() {

        try {

            JSONObject pessoa =
                    fila.getJSONObject(
                            indice
                    );

            String nome =
                    pessoa.optString(
                            "nome",
                            ""
                    );

            txtStatus.setText(
                    (indice + 1)
                    + " de "
                    + fila.length()
                    + " — "
                    + nome
            );

            btnAnterior.setEnabled(
                    indice > 0
            );

            btnProximo.setEnabled(
                    indice
                    < fila.length() - 1
            );

        } catch (Exception erro) {

            erro.printStackTrace();
        }
    }


    private void abrirWhatsapp(
            int posicao
    ) {

        try {

            JSONObject pessoa =
                    fila.getJSONObject(
                            posicao
                    );

            String numero =
                    pessoa.optString(
                            "numero",
                            ""
                    );

            String mensagem =
                    pessoa.optString(
                            "mensagem",
                            ""
                    );

            String url =
                    "whatsapp://send"
                    + "?phone="
                    + numero
                    + "&text="
                    + Uri.encode(
                            mensagem
                    );


            Intent abrir =
                    new Intent(
                            Intent.ACTION_VIEW,
                            Uri.parse(url)
                    );


            abrir.setPackage(
                    "com.whatsapp.w4b"
            );


            abrir.addFlags(
                    Intent.FLAG_ACTIVITY_NEW_TASK
            );


            startActivity(
                    abrir
            );

        } catch (Exception erro) {

            erro.printStackTrace();

            if (txtStatus != null) {

                txtStatus.setText(
                        "Erro ao abrir WhatsApp"
                );
            }
        }
    }


    private void removerOverlay() {

        if (
            overlayView != null
            && windowManager != null
        ) {

            try {

                windowManager.removeView(
                        overlayView
                );

            } catch (Exception ignored) {
            }

            overlayView = null;
        }
    }


    @Override
    public void onDestroy() {

        removerOverlay();

        super.onDestroy();
    }


    @Override
    public IBinder onBind(
            Intent intent
    ) {

        return null;
    }
}
