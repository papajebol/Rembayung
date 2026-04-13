export const formatCurrency = (amount: number) => `RM${amount.toFixed(2)}`;

export const generateOrderId = () => Math.floor(1000 + Math.random() * 9000);
