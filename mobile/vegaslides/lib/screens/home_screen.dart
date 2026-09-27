// ignore_for_file: deprecated_member_use, avoid_print
import 'package:flutter/material.dart';
import 'config_screen.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart'; // Importa a API para buscar os avisos
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';
import '../provider/auth_provider.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final TextEditingController _promptController = TextEditingController();

  @override
  void initState() {
    super.initState();
    // Inicia o radar de avisos silencioso assim que a tela abre
    _checarAvisosStartup();
  }

  @override
  void dispose() {
    _promptController.dispose();
    super.dispose();
  }

  // ==========================================
  // MOTOR DO MEGAFONE (AVISOS)
  // ==========================================
  Future<void> _checarAvisosStartup() async {
    final avisos = await ApiService.buscarAvisos();
    if (avisos.isEmpty) return;

    int maiorId = 0;
    for (var aviso in avisos) {
      int id = aviso['id'] ?? 0;
      if (id > maiorId) maiorId = id;
    }

    final prefs = await SharedPreferences.getInstance();
    int ultimoLido = prefs.getInt('ultimo_aviso_lido') ?? 0;

    // Se a API mandou um aviso novo (ID maior que o salvo), exibe e grava na memória
    if (maiorId > ultimoLido) {
      await prefs.setInt('ultimo_aviso_lido', maiorId);
      if (mounted) {
        _mostrarQuadroAvisos(avisos);
      }
    }
  }

  // O Design da Janela (Estilo Dark/Admin)
  void _mostrarQuadroAvisos(List<dynamic> avisos) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF242424),
        title: const Text('📢 Avisos Importantes', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        content: SizedBox(
          width: double.maxFinite,
          child: ListView.builder(
            shrinkWrap: true,
            itemCount: avisos.length > 10 ? 10 : avisos.length,
            itemBuilder: (c, i) {
              final aviso = avisos[i];
              final tipo = aviso['tipo'] ?? 'info';
              
              // Define a cor da borda baseado no tipo
              Color corBorda = tipo == 'info' ? Colors.blue : 
                               tipo == 'warning' ? Colors.amber : 
                               tipo == 'erro' ? Colors.red : Colors.green;

              return Container(
                margin: const EdgeInsets.only(bottom: 8),
                decoration: BoxDecoration(
                  color: Colors.black12,
                  border: Border(left: BorderSide(color: corBorda, width: 4)),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: ListTile(
                  title: Text(aviso['titulo'] ?? 'Aviso', 
                    style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 14)),
                  subtitle: Text(aviso['mensagem'] ?? '', 
                    style: const TextStyle(color: Colors.white70, fontSize: 13)),
                ),
              );
            },
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Fechar', style: TextStyle(color: Colors.grey)),
          )
        ],
      )
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: Row(
          mainAxisSize: MainAxisSize.min, // Garante que fique centralizado
          children: [
            Image.asset('assets/splash.png', height: 32), // Confirme se o caminho da imagem está correto no pubspec.yaml
            const SizedBox(width: 10),
            const Text('VegaSlides', style: TextStyle(fontWeight: FontWeight.bold)),
          ],
        ),
        backgroundColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
        actions: [
          // Botão manual de Avisos (igual no PC)
          IconButton(
            icon: Icon(Icons.campaign, color: isDark ? Colors.amber : Colors.red),
            onPressed: () async {
              final avisos = await ApiService.buscarAvisos();
              if (mounted && avisos.isNotEmpty) {
                _mostrarQuadroAvisos(avisos);
              } else if (mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Nenhum aviso no momento.')),
                );
              }
            },
          ),
          IconButton(
            icon: Icon(Icons.settings, color: isDark ? Colors.white70 : Colors.black87),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const ConfigScreen()),
              );
            },
          )
        ],
      ),
      body: SingleChildScrollView( // <--- A MÁGICA QUE RESOLVE O ERRO DO TECLADO
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'O que vamos criar hoje?',
              style: TextStyle(
                fontSize: 24, 
                fontWeight: FontWeight.bold, 
                color: isDark ? Colors.white : Colors.black87
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              'Digite o tema e deixe a Inteligência Artificial montar sua apresentação em segundos.',
              style: TextStyle(fontSize: 14, color: isDark ? Colors.white54 : Colors.black54),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 40),
            
            TextField(
              controller: _promptController,
              maxLines: 5,
              style: TextStyle(color: isDark ? Colors.white : Colors.black, fontSize: 16),
              decoration: InputDecoration(
                hintText: 'Ex: Pitch de vendas para um novo app de saúde mental focado em atletas...',
                hintStyle: TextStyle(color: isDark ? Colors.white30 : Colors.black38),
                filled: true,
                fillColor: isDark ? const Color(0xFF141414) : Colors.white,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(16),
                  borderSide: BorderSide.none,
                ),
                contentPadding: const EdgeInsets.all(20),
              ),
            ),
            
            const SizedBox(height: 32),
            
            // Botão Principal
            ElevatedButton(
              onPressed: _promptController.text.trim().isEmpty ? null : () async {
                final auth = Provider.of<AuthProvider>(context, listen: false);
                if (!auth.isAuth) {
                  ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Faça login nas configurações primeiro.')));
                  return;
                }

                // Troca o botão pra tela de carregamento
                showDialog(
                  context: context,
                  barrierDismissible: false,
                  builder: (ctx) => const Center(child: CircularProgressIndicator(color: Color(0xFF8B5CF6))),
                );

                try {
                  final link = await ApiService.gerarApresentacao(auth.token!, _promptController.text.trim());
                  if (mounted) Navigator.pop(context); // Fecha o loading
                  
                  // Abre o link pra baixar o PPTX
                  final url = Uri.parse(link);
                  if (await canLaunchUrl(url)) {
                    await launchUrl(url, mode: LaunchMode.externalApplication);
                  }
                } catch (e) {
                  if (mounted) {
                    Navigator.pop(context); // Fecha o loading
                    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString().replaceAll('Exception: ', '')), backgroundColor: Colors.red));
                  }
                }
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF8B5CF6), // O Roxo VegaTech
                padding: const EdgeInsets.symmetric(vertical: 20),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(16),
                ),
                elevation: 10,
                shadowColor: const Color(0xFF8B5CF6).withOpacity(0.5), // Efeito Glow
              ),
              child: const Text(
                '✨ GERAR APRESENTAÇÃO',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.white,
                  letterSpacing: 1.2,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}