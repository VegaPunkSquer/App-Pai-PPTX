import 'dart:async';
import 'package:flutter/material.dart';
import 'package:vegaslides/services/api_service.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:vegaslides/services/manifesto.dart';

class LojaScreen extends StatefulWidget {
  final String tokenCliente;
  final String filtroLoja;

  const LojaScreen({super.key, required this.tokenCliente, required this.filtroLoja});

  @override
  State<LojaScreen> createState() => _LojaScreenState();
}

class _LojaScreenState extends State<LojaScreen> {
  bool _carregando = true;
  String _moedaSelecionada = 'BRL';
  Map<String, dynamic> _vitrine = {};
  final _cupomController = TextEditingController();
  
  bool _processandoCheckout = false;
  String _statusMsg = "";
  Timer? _radarPagamento;

  @override
  void initState() {
    super.initState();
    _carregarPlanos();
  }

  @override
  void dispose() {
    _cupomController.dispose();
    _radarPagamento?.cancel();
    super.dispose();
  }

  Future<void> _carregarPlanos() async {
    setState(() => _carregando = true);
    
    // MÁGICA: Lê os planos do manifesto local instantaneamente
    final todosPlanos = Manifesto.planosPrecos;
    final gatewayAlvo = _moedaSelecionada == 'USD' ? 'stripe' : 'asaas';
    
    Map<String, dynamic> planosFiltrados = {};
    todosPlanos.forEach((key, value) {
      if (value['gateway'] == gatewayAlvo) {
        planosFiltrados[key] = value;
      }
    });

    setState(() {
      _vitrine = planosFiltrados;
      _carregando = false;
    });
  }

  Future<void> _comprarPlano(String planoNome) async {
    setState(() {
      _processandoCheckout = true;
      _statusMsg = "Gerando ambiente seguro...";
    });

    final gateway = _moedaSelecionada == 'USD' ? 'stripe' : 'asaas';
    final cupom = _cupomController.text.trim();

    try {
      final dados = await ApiService.gerarCheckout(widget.tokenCliente, planoNome, cupom, gateway);
      
      // Se for cupom de 100%, libera na hora
      if (dados['gratuito'] == true) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Acesso VIP liberado com sucesso!'), backgroundColor: Colors.green),
          );
          Navigator.pop(context, planoNome); // Volta enviando qual plano comprou
        }
        return;
      }

      // Se for compra real, abre o navegador e liga o radar
      final checkoutUrl = dados['checkout_url'];
      final cobrancaId = dados['cobranca_id'];

      if (checkoutUrl != null) {
        final url = Uri.parse(checkoutUrl);
        if (await canLaunchUrl(url)) {
          await launchUrl(url, mode: LaunchMode.externalApplication);
          setState(() => _statusMsg = "Aguardando confirmação do pagamento...");
          _iniciarRadar(cobrancaId, planoNome);
        } else {
          throw Exception("Não foi possível abrir o navegador.");
        }
      }
    } catch (e) {
      if (mounted) {
        showDialog(
          context: context,
          builder: (ctx) => AlertDialog(
            title: const Text('Erro no Checkout'),
            content: Text(e.toString().replaceAll('Exception: ', '')),
            actions: [
              TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('OK'))
            ],
          )
        );
      }
      setState(() {
        _processandoCheckout = false;
        _statusMsg = "";
      });
    }
  }

  void _iniciarRadar(String cobrancaId, String planoComprado) {
    _radarPagamento?.cancel();
    _radarPagamento = Timer.periodic(const Duration(seconds: 5), (timer) async {
      final pago = await ApiService.checarStatusPagamento(cobrancaId);
      if (pago && mounted) {
        timer.cancel();
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Pagamento Confirmado! Acesso Liberado.'), backgroundColor: Colors.green),
        );
        Navigator.pop(context, planoComprado); // Sucesso! Fecha a loja e destranca o app
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('🛒 Loja VegaTech', style: TextStyle(fontWeight: FontWeight.bold)),
        elevation: 0,
      ),
      body: _carregando
          ? Center(child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const CircularProgressIndicator(),
                const SizedBox(height: 16),
                Text(_statusMsg, style: const TextStyle(fontWeight: FontWeight.bold))
              ],
            ))
          : Column(
              children: [
                // Filtro de Moeda e Cupom
                Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text('Moeda:', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                          DropdownButton<String>(
                            value: _moedaSelecionada,
                            items: const [
                              DropdownMenuItem(value: 'BRL', child: Text('BRL (R\$) - Brasil')),
                              DropdownMenuItem(value: 'USD', child: Text('USD (\$) - Internacional')),
                            ],
                            onChanged: _processandoCheckout ? null : (val) {
                              if (val != null) {
                                _moedaSelecionada = val;
                                _carregarPlanos();
                              }
                            },
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      TextField(
                        controller: _cupomController,
                        decoration: InputDecoration(
                          labelText: 'Cupom de Desconto (Opcional)',
                          prefixIcon: const Icon(Icons.local_offer),
                          border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                          contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8)
                        ),
                        enabled: !_processandoCheckout,
                      ),
                    ],
                  ),
                ),
                
                if (_processandoCheckout && _statusMsg.isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.all(8.0),
                    child: Text(_statusMsg, style: const TextStyle(color: Colors.blue, fontWeight: FontWeight.bold)),
                  ),

                // Lista de Planos
                Expanded(
                  child: _vitrine.isEmpty
                    ? const Center(child: Text("Nenhum plano disponível."))
                    : ListView(
                        padding: const EdgeInsets.all(16),
                        children: _vitrine.entries.where((entry) {
                          // O seu Filtro Absoluto VegaTech
                          final nome = entry.key.toUpperCase();
                          if (widget.filtroLoja == "BYOK" && !nome.contains("BYOK")) return false;
                          if (widget.filtroLoja == "SAAS" && nome.contains("BYOK")) return false;
                          if (widget.filtroLoja == "ELITE" && !nome.contains("ELITE")) return false;
                          return true;
                        }).map((entry) {
                          final nomePlano = entry.key;
                          final detalhes = entry.value;
                          final valor = detalhes['valor'] ?? 0.0;
                          final ciclo = detalhes['ciclo'] ?? 'unico';
                          final trialDias = detalhes['trial_dias'] ?? 0;
                          
                          final nomeExibicao = nomePlano.split('_')[0];
                          final isUsd = _moedaSelecionada == 'USD';

                          return Card(
                            elevation: 4,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                            margin: const EdgeInsets.only(bottom: 16),
                            child: Padding(
                              padding: const EdgeInsets.all(16.0),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.stretch,
                                children: [
                                  Text("⭐ ${nomeExibicao.toUpperCase()}", style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                                  const SizedBox(height: 8),
                                  Text(
                                    "${isUsd ? '\$' : 'R\$'} ${valor.toStringAsFixed(2)} ${ciclo != 'unico' ? '/ ${ciclo.toUpperCase()}' : ''}",
                                    style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w900, color: Colors.green),
                                  ),
                                  if (trialDias > 0) ...[
                                    const SizedBox(height: 8),
                                    Container(
                                      padding: const EdgeInsets.symmetric(vertical: 4),
                                      decoration: BoxDecoration(
                                        color: Colors.amber.withValues(alpha: 0.2),
                                        borderRadius: BorderRadius.circular(4),
                                        border: Border.all(color: Colors.amber)
                                      ),
                                      child: Text("🎁 $trialDias DIAS TOTALMENTE GRÁTIS!", textAlign: TextAlign.center, style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.amber)),
                                    )
                                  ],
                                  const SizedBox(height: 16),
                                  ElevatedButton(
                                    onPressed: _processandoCheckout ? null : () => _comprarPlano(nomePlano),
                                    style: ElevatedButton.styleFrom(
                                      backgroundColor: Colors.blue,
                                      padding: const EdgeInsets.symmetric(vertical: 12),
                                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8))
                                    ),
                                    child: const Text("ASSINAR AGORA", style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                                  )
                                ],
                              ),
                            ),
                          );
                        }).toList(),
                      ),
                ),
              ],
            ),
    );
  }
}